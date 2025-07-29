import java.util.*;
import java.util.concurrent.*;

public class TransactionCoordinator {
    // Stores the state of transactions and their associated participants.
    private final Map<String, List<Participant>> transactions = new ConcurrentHashMap<>();
    // Timeout for participant responses in milliseconds.
    private final long timeoutMillis = 500;

    // Executes a distributed transaction using the Two-Phase Commit protocol.
    // Returns true if the transaction commits; false if it is rolled back.
    public boolean executeTransaction(String transactionId, List<Participant> participants) {
        transactions.put(transactionId, participants);
        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        List<Future<String>> futures = new ArrayList<>();

        for (Participant participant : participants) {
            Future<String> future = executor.submit(participant::prepare);
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<String> future : futures) {
            try {
                String response = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!"prepared".equals(response)) {
                    allPrepared = false;
                }
            } catch (TimeoutException | InterruptedException | ExecutionException e) {
                allPrepared = false;
            }
        }

        if (allPrepared) {
            for (Participant participant : participants) {
                participant.commit();
            }
        } else {
            for (Participant participant : participants) {
                participant.rollback();
            }
        }

        executor.shutdown();
        return allPrepared;
    }

    // Recovers an in-progress transaction after a crash.
    // If all participants are in a prepared state, it commits them; otherwise, it rolls them back.
    public boolean recoverAndExecute(String transactionId) {
        List<Participant> participants = transactions.get(transactionId);
        if (participants == null) {
            return false;
        }
        boolean allPrepared = participants.stream().allMatch(Participant::isPrepared);
        if (allPrepared) {
            for (Participant participant : participants) {
                participant.commit();
            }
            return true;
        } else {
            for (Participant participant : participants) {
                participant.rollback();
            }
            return false;
        }
    }
    
    // Clears the transaction state for the given transaction ID.
    public void clearTransaction(String transactionId) {
        transactions.remove(transactionId);
    }
}