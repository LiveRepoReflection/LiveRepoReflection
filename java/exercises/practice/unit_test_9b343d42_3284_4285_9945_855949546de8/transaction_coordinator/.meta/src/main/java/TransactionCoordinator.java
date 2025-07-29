package transaction_coordinator;

import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import java.util.concurrent.*;

public class TransactionCoordinator {

    private static final int TIMEOUT_PREPARE_MS = 300;
    private static final int TIMEOUT_COMMIT_MS = 300;
    private static final int TIMEOUT_ROLLBACK_MS = 300;
    private static final int MAX_RETRIES = 3;

    private final List<String> logs = new ArrayList<>();
    private final ExecutorService executor = Executors.newCachedThreadPool();

    public boolean executeTransaction(String transactionId, Map<String, ParticipantService> services, Map<String, String> operations) {
        log("Transaction " + transactionId + " start");

        // Prepare Phase
        ConcurrentMap<String, String> votes = new ConcurrentHashMap<>();
        boolean prepareSuccess = true;
        List<Future<Boolean>> prepareFutures = new ArrayList<>();
        for (Map.Entry<String, ParticipantService> entry : services.entrySet()) {
            String serviceId = entry.getKey();
            ParticipantService service = entry.getValue();
            String operation = operations.get(serviceId);
            Future<Boolean> future = executor.submit(() -> {
                for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
                    try {
                        Callable<String> action = () -> service.prepare(transactionId, operation);
                        String vote = callWithTimeout(action, TIMEOUT_PREPARE_MS);
                        log("Service " + serviceId + " prepared with vote: " + vote);
                        votes.put(serviceId, vote);
                        return vote.equalsIgnoreCase("commit");
                    } catch (Exception e) {
                        log("Service " + serviceId + " prepare attempt " + attempt + " failed: " + e.getMessage());
                        if (attempt == MAX_RETRIES) {
                            return false;
                        }
                    }
                }
                return false;
            });
            prepareFutures.add(future);
        }
        try {
            for (Future<Boolean> future : prepareFutures) {
                if (!future.get()) {
                    prepareSuccess = false;
                    break;
                }
            }
        } catch (Exception e) {
            log("Exception during prepare phase: " + e.getMessage());
            prepareSuccess = false;
        }

        if (!prepareSuccess) {
            log("Transaction " + transactionId + " prepare phase failed, initiating rollback.");
            rollbackAll(transactionId, services);
            log("Transaction " + transactionId + " rolled back.");
            return false;
        }

        // Commit Phase
        boolean commitSuccess = true;
        List<Future<Boolean>> commitFutures = new ArrayList<>();
        for (Map.Entry<String, ParticipantService> entry : services.entrySet()) {
            String serviceId = entry.getKey();
            ParticipantService service = entry.getValue();
            Future<Boolean> future = executor.submit(() -> {
                for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
                    try {
                        Runnable action = () -> {
                            try {
                                service.commit(transactionId);
                            } catch (Exception ex) {
                                throw new RuntimeException(ex);
                            }
                        };
                        runWithTimeout(action, TIMEOUT_COMMIT_MS);
                        log("Service " + serviceId + " committed.");
                        return true;
                    } catch (Exception e) {
                        log("Service " + serviceId + " commit attempt " + attempt + " failed: " + e.getMessage());
                        if (attempt == MAX_RETRIES) {
                            return false;
                        }
                    }
                }
                return false;
            });
            commitFutures.add(future);
        }
        try {
            for (Future<Boolean> future : commitFutures) {
                if (!future.get()) {
                    commitSuccess = false;
                    break;
                }
            }
        } catch (Exception e) {
            log("Exception during commit phase: " + e.getMessage());
            commitSuccess = false;
        }

        if (!commitSuccess) {
            log("Transaction " + transactionId + " commit phase failed, initiating rollback.");
            rollbackAll(transactionId, services);
            log("Transaction " + transactionId + " rolled back.");
            return false;
        }

        log("Transaction " + transactionId + " committed successfully.");
        return true;
    }

    private void rollbackAll(String transactionId, Map<String, ParticipantService> services) {
        List<Future<Boolean>> rollbackFutures = new ArrayList<>();
        for (Map.Entry<String, ParticipantService> entry : services.entrySet()) {
            String serviceId = entry.getKey();
            ParticipantService service = entry.getValue();
            Future<Boolean> future = executor.submit(() -> {
                for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
                    try {
                        Runnable action = () -> {
                            try {
                                service.rollback(transactionId);
                            } catch (Exception ex) {
                                throw new RuntimeException(ex);
                            }
                        };
                        runWithTimeout(action, TIMEOUT_ROLLBACK_MS);
                        log("Service " + serviceId + " rolled back.");
                        return true;
                    } catch (Exception e) {
                        log("Service " + serviceId + " rollback attempt " + attempt + " failed: " + e.getMessage());
                        if (attempt == MAX_RETRIES) {
                            return false;
                        }
                    }
                }
                return false;
            });
            rollbackFutures.add(future);
        }
        for (Future<Boolean> future : rollbackFutures) {
            try {
                future.get();
            } catch (Exception e) {
                log("Exception during rollback: " + e.getMessage());
            }
        }
    }

    private <T> T callWithTimeout(Callable<T> callable, int timeoutMs) throws Exception {
        Future<T> future = executor.submit(callable);
        return future.get(timeoutMs, TimeUnit.MILLISECONDS);
    }

    private void runWithTimeout(Runnable runnable, int timeoutMs) throws Exception {
        Future<?> future = executor.submit(runnable);
        future.get(timeoutMs, TimeUnit.MILLISECONDS);
    }

    private synchronized void log(String message) {
        logs.add(message);
        System.out.println(message);
    }

    public List<String> getLogs() {
        return logs;
    }
}