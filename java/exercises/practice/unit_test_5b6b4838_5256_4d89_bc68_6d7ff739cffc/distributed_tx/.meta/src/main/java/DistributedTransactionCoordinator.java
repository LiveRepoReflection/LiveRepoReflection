import java.util.List;
import java.util.concurrent.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ConcurrentHashMap;

public class DistributedTransactionCoordinator {
    private final ConcurrentHashMap<String, Boolean> transactionResults = new ConcurrentHashMap<>();
    private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public boolean executeTransaction(String transactionId, List<ParticipantService> participants, long timeoutMillis) {
        if (transactionResults.containsKey(transactionId)) {
            log("Transaction " + transactionId + " already processed with result: " + transactionResults.get(transactionId));
            return transactionResults.get(transactionId);
        }

        log("Starting transaction: " + transactionId);

        ExecutorService executor = Executors.newFixedThreadPool(participants.size());
        boolean prepareSuccess = true;

        // Prepare Phase
        try {
            List<Future<Boolean>> prepareFutures = new CopyOnWriteArrayList<>();
            for (ParticipantService participant : participants) {
                Future<Boolean> future = executor.submit(() -> {
                    log("Sending prepare to participant: " + participant.toString() + " for transaction " + transactionId);
                    boolean result = participant.prepare(transactionId);
                    log("Received prepare response: " + result + " from participant: " + participant.toString() + " for transaction " + transactionId);
                    return result;
                });
                prepareFutures.add(future);
            }
            // Collect responses with timeout
            for (Future<Boolean> future : prepareFutures) {
                try {
                    boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!result) {
                        prepareSuccess = false;
                    }
                } catch (TimeoutException e) {
                    log("Timeout during prepare phase for transaction " + transactionId);
                    prepareSuccess = false;
                } catch (Exception e) {
                    log("Exception during prepare phase for transaction " + transactionId + ": " + e.getMessage());
                    prepareSuccess = false;
                }
            }
        } finally {
            // Continue to check prepare success.
        }

        if (!prepareSuccess) {
            log("Prepare phase failed for transaction " + transactionId + ". Initiating rollback.");
            performRollback(transactionId, participants, timeoutMillis);
            transactionResults.put(transactionId, false);
            executor.shutdownNow();
            return false;
        }

        // Commit Phase
        boolean commitSuccess = true;
        try {
            List<Future<Boolean>> commitFutures = new CopyOnWriteArrayList<>();
            for (ParticipantService participant : participants) {
                Future<Boolean> future = executor.submit(() -> {
                    log("Sending commit to participant: " + participant.toString() + " for transaction " + transactionId);
                    boolean result = participant.commit(transactionId);
                    log("Received commit response: " + result + " from participant: " + participant.toString() + " for transaction " + transactionId);
                    return result;
                });
                commitFutures.add(future);
            }
            for (Future<Boolean> future : commitFutures) {
                try {
                    boolean result = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                    if (!result) {
                        commitSuccess = false;
                    }
                } catch (TimeoutException e) {
                    log("Timeout during commit phase for transaction " + transactionId);
                    commitSuccess = false;
                } catch (Exception e) {
                    log("Exception during commit phase for transaction " + transactionId + ": " + e.getMessage());
                    commitSuccess = false;
                }
            }
        } finally {
            if (!commitSuccess) {
                log("Commit phase failed for transaction " + transactionId + ". Initiating rollback.");
                performRollback(transactionId, participants, timeoutMillis);
                transactionResults.put(transactionId, false);
                executor.shutdownNow();
                return false;
            }
        }

        log("Transaction " + transactionId + " committed successfully.");
        transactionResults.put(transactionId, true);
        executor.shutdownNow();
        return true;
    }

    private void performRollback(String transactionId, List<ParticipantService> participants, long timeoutMillis) {
        ExecutorService rollbackExecutor = Executors.newFixedThreadPool(participants.size());
        try {
            List<Future<Boolean>> rollbackFutures = new CopyOnWriteArrayList<>();
            for (ParticipantService participant : participants) {
                Future<Boolean> future = rollbackExecutor.submit(() -> {
                    log("Sending rollback to participant: " + participant.toString() + " for transaction " + transactionId);
                    boolean result = participant.rollback(transactionId);
                    log("Received rollback response: " + result + " from participant: " + participant.toString() + " for transaction " + transactionId);
                    return result;
                });
                rollbackFutures.add(future);
            }
            for (Future<Boolean> future : rollbackFutures) {
                try {
                    future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                } catch (Exception e) {
                    log("Exception/Timeout during rollback phase for transaction " + transactionId + ": " + e.getMessage());
                }
            }
        } finally {
            rollbackExecutor.shutdownNow();
        }
    }

    private void log(String message) {
        System.out.println(LocalDateTime.now().format(formatter) + " - " + message);
    }
}