import java.util.*;
import java.util.concurrent.*;
import java.util.function.Function;

public class TransactionCoordinator {
    // Map to hold transaction id and its associated participants.
    private final ConcurrentMap<String, Set<String>> transactionParticipants = new ConcurrentHashMap<>();
    // Executor service to run participant actions concurrently.
    private final ExecutorService executor = Executors.newCachedThreadPool();
    // Timeout value for the prepare phase in seconds.
    private final long TIMEOUT_SECONDS = 5;

    public enum TransactionResult {
        COMMIT, ROLLBACK
    }

    /**
     * Initiates a new distributed transaction by registering the provided participants.
     * 
     * @param participants a set of participant identifiers
     * @return a unique transaction id
     */
    public String beginTransaction(Set<String> participants) {
        String transactionId = UUID.randomUUID().toString();
        transactionParticipants.put(transactionId, new HashSet<>(participants));
        System.out.println("Transaction " + transactionId + " started with participants: " + participants);
        return transactionId;
    }

    /**
     * Executes the distributed transaction using the Two-Phase Commit (2PC) protocol.
     * The method first performs a prepare phase, and if all participants vote commit, 
     * it proceeds with the commit phase; otherwise, it rolls back the transaction.
     * 
     * @param transactionId the transaction identifier
     * @param participantActions a mapping of participant id to their action functions.
     * @return the overall transaction result (COMMIT or ROLLBACK)
     */
    public TransactionResult executeTransaction(String transactionId, Map<String, Function<String, String>> participantActions) {
        Set<String> participants = transactionParticipants.get(transactionId);
        if (participants == null || participants.isEmpty()) {
            System.out.println("Transaction " + transactionId + " has no registered participants.");
            return TransactionResult.ROLLBACK;
        }

        System.out.println("Executing transaction " + transactionId + " with participants: " + participants);

        // Prepare phase: send "prepare" message concurrently to each participant.
        Map<String, Future<String>> futureMap = new HashMap<>();
        for (String participant : participants) {
            Function<String, String> action = participantActions.get(participant);
            if (action == null) {
                // If no action is defined for a participant, treat as vote_rollback.
                System.out.println("No action defined for participant " + participant + ", treating as vote_rollback.");
                CompletableFuture<String> future = new CompletableFuture<>();
                future.complete("vote_rollback");
                futureMap.put(participant, future);
            } else {
                Future<String> future = executor.submit(() -> {
                    try {
                        return action.apply("prepare");
                    } catch (Exception e) {
                        System.out.println("Exception during prepare for participant " + participant + ": " + e.getMessage());
                        return "vote_rollback";
                    }
                });
                futureMap.put(participant, future);
            }
        }

        boolean allCommit = true;
        for (Map.Entry<String, Future<String>> entry : futureMap.entrySet()) {
            String participant = entry.getKey();
            Future<String> future = entry.getValue();
            String vote;
            try {
                vote = future.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                System.out.println("Timeout or exception for participant " + participant + ": " + e.getMessage());
                vote = "vote_rollback";
            }
            System.out.println("Participant " + participant + " voted: " + vote);
            if (!"vote_commit".equalsIgnoreCase(vote)) {
                allCommit = false;
            }
        }

        TransactionResult result = allCommit ? TransactionResult.COMMIT : TransactionResult.ROLLBACK;
        System.out.println("Transaction " + transactionId + " final decision: " + result);

        // Commit/Rollback phase: notify participants of the final decision.
        for (String participant : participants) {
            Function<String, String> action = participantActions.get(participant);
            if (action != null) {
                try {
                    String response = action.apply(result == TransactionResult.COMMIT ? "commit" : "rollback");
                    System.out.println("Participant " + participant + " acknowledged: " + response);
                } catch (Exception e) {
                    System.out.println("Exception during " + (result == TransactionResult.COMMIT ? "commit" : "rollback") +
                            " for participant " + participant + ": " + e.getMessage());
                }
            } else {
                System.out.println("No action defined for participant " + participant + " during " +
                        (result == TransactionResult.COMMIT ? "commit" : "rollback") + " phase.");
            }
        }

        // Remove the transaction entry.
        transactionParticipants.remove(transactionId);

        // Idempotency Note:
        // In a production system, commit/rollback operations would be recorded in a persistent log to ensure idempotency.
        // If the same commit/rollback message is received more than once, the system would recognize the transaction state
        // and avoid reprocessing, thereby ensuring safe duplicate handling.

        return result;
    }
}