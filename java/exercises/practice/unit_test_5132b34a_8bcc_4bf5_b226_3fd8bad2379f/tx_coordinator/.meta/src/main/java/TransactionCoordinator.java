import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionCoordinator {
    private final Map<String, Set<Participant>> transactionParticipants = new ConcurrentHashMap<>();
    private final Set<Participant> enrolledParticipants = Collections.synchronizedSet(new HashSet<>());
    private final AtomicInteger transactionCounter = new AtomicInteger(0);
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public String beginTransaction() {
        return "TX-" + transactionCounter.incrementAndGet();
    }

    public void enroll(String transactionId, Participant participant) {
        Objects.requireNonNull(transactionId, "Transaction ID cannot be null");
        Objects.requireNonNull(participant, "Participant cannot be null");

        synchronized (enrolledParticipants) {
            if (enrolledParticipants.contains(participant)) {
                throw new IllegalStateException("Participant already enrolled in another transaction");
            }
            enrolledParticipants.add(participant);
        }

        transactionParticipants.computeIfAbsent(transactionId, k -> Collections.synchronizedSet(new HashSet<>()))
                             .add(participant);
    }

    public boolean commitTransaction(String transactionId) {
        Set<Participant> participants = transactionParticipants.get(transactionId);
        if (participants == null || participants.isEmpty()) {
            return true;
        }

        try {
            // Phase 1: Prepare
            List<Future<Boolean>> prepareResults = new ArrayList<>();
            for (Participant p : participants) {
                prepareResults.add(executor.submit(() -> p.prepare(transactionId)));
            }

            boolean allPrepared = true;
            for (Future<Boolean> result : prepareResults) {
                try {
                    if (!result.get()) {
                        allPrepared = false;
                        break;
                    }
                } catch (Exception e) {
                    allPrepared = false;
                    break;
                }
            }

            // Phase 2: Commit or Rollback
            if (allPrepared) {
                boolean commitSuccess = true;
                for (Participant p : participants) {
                    try {
                        p.commit(transactionId);
                    } catch (Exception e) {
                        commitSuccess = false;
                        break;
                    }
                }

                if (!commitSuccess) {
                    rollbackParticipants(transactionId, participants);
                    return false;
                }
            } else {
                rollbackParticipants(transactionId, participants);
                return false;
            }

            return true;
        } finally {
            cleanupTransaction(transactionId, participants);
        }
    }

    public boolean rollbackTransaction(String transactionId) {
        Set<Participant> participants = transactionParticipants.get(transactionId);
        if (participants == null || participants.isEmpty()) {
            return true;
        }

        try {
            return rollbackParticipants(transactionId, participants);
        } finally {
            cleanupTransaction(transactionId, participants);
        }
    }

    private boolean rollbackParticipants(String transactionId, Set<Participant> participants) {
        boolean allRolledBack = true;
        for (Participant p : participants) {
            try {
                p.rollback(transactionId);
            } catch (Exception e) {
                allRolledBack = false;
            }
        }
        return allRolledBack;
    }

    private void cleanupTransaction(String transactionId, Set<Participant> participants) {
        if (participants != null) {
            synchronized (enrolledParticipants) {
                enrolledParticipants.removeAll(participants);
            }
            transactionParticipants.remove(transactionId);
        }
    }

    public void shutdown() {
        executor.shutdown();
    }
}