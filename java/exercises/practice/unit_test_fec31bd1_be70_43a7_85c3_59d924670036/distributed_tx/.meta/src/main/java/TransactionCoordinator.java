import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.logging.Logger;

public class TransactionCoordinator {
    private static final Logger logger = Logger.getLogger(TransactionCoordinator.class.getName());
    private final List<Microservice> enlistedMicroservices = new ArrayList<>();
    private final ExecutorService executorService;
    private final int maxRetryAttempts;

    public TransactionCoordinator(int maxRetryAttempts) {
        this.maxRetryAttempts = maxRetryAttempts;
        this.executorService = Executors.newCachedThreadPool();
    }

    public TransactionContext begin() {
        UUID transactionId = UUID.randomUUID();
        logger.info("Beginning transaction: " + transactionId);
        return new TransactionContext(transactionId);
    }

    public synchronized void enlist(Microservice microservice) {
        enlistedMicroservices.add(microservice);
    }

    public boolean prepareTransaction(TransactionContext context) {
        List<Future<Boolean>> futures = new ArrayList<>();
        AtomicBoolean allPrepared = new AtomicBoolean(true);

        for (Microservice ms : enlistedMicroservices) {
            futures.add(executorService.submit(() -> {
                for (int attempt = 0; attempt < maxRetryAttempts; attempt++) {
                    try {
                        boolean prepared = ms.prepare(context);
                        if (!prepared) {
                            allPrepared.set(false);
                        }
                        return prepared;
                    } catch (Exception e) {
                        logger.warning("Prepare attempt " + (attempt + 1) + " failed for transaction " + 
                            context.getTransactionId() + ": " + e.getMessage());
                        if (attempt == maxRetryAttempts - 1) {
                            allPrepared.set(false);
                            return false;
                        }
                    }
                }
                return false;
            }));
        }

        try {
            for (Future<Boolean> future : futures) {
                future.get();
            }
        } catch (InterruptedException | ExecutionException e) {
            logger.severe("Error during prepare phase: " + e.getMessage());
            allPrepared.set(false);
        }

        return allPrepared.get();
    }

    public boolean commitTransaction(TransactionContext context) {
        List<Future<Void>> futures = new ArrayList<>();
        AtomicBoolean allCommitted = new AtomicBoolean(true);

        for (Microservice ms : enlistedMicroservices) {
            futures.add(executorService.submit(() -> {
                for (int attempt = 0; attempt < maxRetryAttempts; attempt++) {
                    try {
                        ms.commit(context);
                        return null;
                    } catch (Exception e) {
                        logger.warning("Commit attempt " + (attempt + 1) + " failed for transaction " + 
                            context.getTransactionId() + ": " + e.getMessage());
                        if (attempt == maxRetryAttempts - 1) {
                            allCommitted.set(false);
                            return null;
                        }
                    }
                }
                return null;
            }));
        }

        try {
            for (Future<Void> future : futures) {
                future.get();
            }
        } catch (InterruptedException | ExecutionException e) {
            logger.severe("Error during commit phase: " + e.getMessage());
            allCommitted.set(false);
        }

        return allCommitted.get();
    }

    public boolean rollbackTransaction(TransactionContext context) {
        List<Future<Void>> futures = new ArrayList<>();
        AtomicBoolean allRolledBack = new AtomicBoolean(true);

        for (Microservice ms : enlistedMicroservices) {
            futures.add(executorService.submit(() -> {
                for (int attempt = 0; attempt < maxRetryAttempts; attempt++) {
                    try {
                        ms.rollback(context);
                        return null;
                    } catch (Exception e) {
                        logger.warning("Rollback attempt " + (attempt + 1) + " failed for transaction " + 
                            context.getTransactionId() + ": " + e.getMessage());
                        if (attempt == maxRetryAttempts - 1) {
                            allRolledBack.set(false);
                            return null;
                        }
                    }
                }
                return null;
            }));
        }

        try {
            for (Future<Void> future : futures) {
                future.get();
            }
        } catch (InterruptedException | ExecutionException e) {
            logger.severe("Error during rollback phase: " + e.getMessage());
            allRolledBack.set(false);
        }

        return allRolledBack.get();
    }

    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}