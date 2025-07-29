import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TransactionManager {
    private static final int PREPARE_TIMEOUT_MS = 1000;
    private static final int MAX_RETRIES = 3;
    private static final int INITIAL_BACKOFF_MS = 100;

    private final Map<String, Service> services;
    private final ExecutorService executorService;

    public TransactionManager(Map<String, Service> services) {
        this.services = services;
        this.executorService = Executors.newFixedThreadPool(
            Runtime.getRuntime().availableProcessors() * 2
        );
    }

    public CompletableFuture<Boolean> executeTransaction(Transaction transaction) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return executeTransactionInternal(transaction);
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        }, executorService);
    }

    private boolean executeTransactionInternal(Transaction transaction) {
        // Phase 1: Prepare
        boolean prepareSuccess = preparePhase(transaction);
        
        // Phase 2: Commit or Rollback
        if (prepareSuccess) {
            return commitPhase(transaction);
        } else {
            rollbackPhase(transaction);
            throw new CompletionException(
                new RuntimeException("Transaction rolled back: " + transaction.getId())
            );
        }
    }

    private boolean preparePhase(Transaction transaction) {
        Map<String, CompletableFuture<Boolean>> prepareFutures = new ConcurrentHashMap<>();

        // Send prepare requests to all participating services
        for (Map.Entry<String, String> entry : transaction.getOperations().entrySet()) {
            String serviceId = entry.getKey();
            String operation = entry.getValue();
            Service service = services.get(serviceId);

            prepareFutures.put(serviceId, prepareWithRetry(service, transaction.getId(), operation));
        }

        try {
            // Wait for all prepare responses
            CompletableFuture<Void> allPrepares = CompletableFuture.allOf(
                prepareFutures.values().toArray(new CompletableFuture[0])
            );

            allPrepares.get(PREPARE_TIMEOUT_MS, TimeUnit.MILLISECONDS);

            // Check if all services voted to commit
            return prepareFutures.values().stream()
                .allMatch(future -> {
                    try {
                        return future.get();
                    } catch (Exception e) {
                        return false;
                    }
                });
        } catch (TimeoutException e) {
            throw new CompletionException(
                new RuntimeException("Transaction timed out: " + transaction.getId())
            );
        } catch (Exception e) {
            return false;
        }
    }

    private CompletableFuture<Boolean> prepareWithRetry(
        Service service, 
        String txId, 
        String operation
    ) {
        return CompletableFuture.supplyAsync(() -> {
            AtomicInteger attempts = new AtomicInteger(0);
            while (attempts.get() < MAX_RETRIES) {
                try {
                    if (service.prepare(txId, operation)) {
                        return true;
                    }
                    // Exponential backoff
                    Thread.sleep(INITIAL_BACKOFF_MS * (1L << attempts.get()));
                    attempts.incrementAndGet();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
            return false;
        }, executorService);
    }

    private boolean commitPhase(Transaction transaction) {
        for (String serviceId : transaction.getOperations().keySet()) {
            Service service = services.get(serviceId);
            try {
                service.commit(transaction.getId());
            } catch (Exception e) {
                // Log error but continue with other services
                // Since prepare was successful, we assume commit will eventually succeed
                continue;
            }
        }
        return true;
    }

    private void rollbackPhase(Transaction transaction) {
        for (String serviceId : transaction.getOperations().keySet()) {
            Service service = services.get(serviceId);
            try {
                service.rollback(transaction.getId());
            } catch (Exception e) {
                // Log error but continue with other services
                continue;
            }
        }
    }

    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}