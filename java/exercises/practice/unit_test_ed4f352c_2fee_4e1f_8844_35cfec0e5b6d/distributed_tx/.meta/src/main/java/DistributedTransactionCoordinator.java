import java.util.UUID;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

public class DistributedTransactionCoordinator {

    private final ConcurrentMap<String, List<TransactionParticipant>> transactions;
    private final ExecutorService executor;
    private static final int PREPARE_TIMEOUT_MS = 1000;
    private static final int COMMIT_TIMEOUT_MS = 1000;

    public DistributedTransactionCoordinator() {
        transactions = new ConcurrentHashMap<>();
        // Create a fixed thread pool based on available processors.
        executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
    }

    public String beginTransaction() {
        String txId = UUID.randomUUID().toString();
        transactions.put(txId, new ArrayList<>());
        return txId;
    }

    public void registerParticipant(String txId, TransactionParticipant participant) {
        List<TransactionParticipant> participants = transactions.get(txId);
        if (participants != null) {
            synchronized (participants) {
                participants.add(participant);
            }
        }
    }

    public boolean executeTransaction(String txId) {
        List<TransactionParticipant> participants = transactions.remove(txId);
        if (participants == null || participants.isEmpty()) {
            return false;
        }

        boolean allPrepared = true;
        // Prepare Phase
        for (TransactionParticipant participant : participants) {
            Future<Boolean> future = executor.submit(() -> participant.prepare());
            try {
                Boolean result = future.get(PREPARE_TIMEOUT_MS, TimeUnit.MILLISECONDS);
                if (result == null || !result) {
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                allPrepared = false;
                break;
            }
        }

        // Commit or Rollback Phase
        if (allPrepared) {
            List<Future<?>> commitFutures = new ArrayList<>();
            for (TransactionParticipant participant : participants) {
                commitFutures.add(executor.submit(() -> {
                    participant.commit();
                    return null;
                }));
            }
            // Optionally, wait for commit tasks to complete
            for (Future<?> f : commitFutures) {
                try {
                    f.get(COMMIT_TIMEOUT_MS, TimeUnit.MILLISECONDS);
                } catch (Exception e) {
                    // In real-world, you'd handle partial commit failures
                }
            }
            return true;
        } else {
            List<Future<?>> rollbackFutures = new ArrayList<>();
            for (TransactionParticipant participant : participants) {
                rollbackFutures.add(executor.submit(() -> {
                    participant.rollback();
                    return null;
                }));
            }
            // Wait for rollback tasks to complete
            for (Future<?> f : rollbackFutures) {
                try {
                    f.get(COMMIT_TIMEOUT_MS, TimeUnit.MILLISECONDS);
                } catch (Exception e) {
                    // In real-world, you'd log errors for failed rollbacks
                }
            }
            return false;
        }
    }

    public void shutdown() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}