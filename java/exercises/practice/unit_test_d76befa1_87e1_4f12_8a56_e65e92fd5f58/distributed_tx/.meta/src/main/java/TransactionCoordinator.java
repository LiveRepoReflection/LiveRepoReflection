import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.*;

public class TransactionCoordinator {
    private static final Logger logger = LoggerFactory.getLogger(TransactionCoordinator.class);
    private static final int PREPARE_TIMEOUT_SECONDS = 5;
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_BACKOFF_MILLIS = 100;

    private final ExecutorService executor;

    public TransactionCoordinator() {
        this.executor = Executors.newCachedThreadPool();
    }

    public TransactionContext begin() {
        String transactionId = UUID.randomUUID().toString();
        logger.info("Starting transaction: {}", transactionId);
        return new TransactionContext(transactionId);
    }

    public void commit(List<Service> services, TransactionContext context) {
        logger.info("Starting prepare phase for transaction: {}", context.getTransactionId());
        List<Future<Boolean>> futures = new ArrayList<>();
        for (Service s : services) {
            Future<Boolean> future = executor.submit(() -> {
                try {
                    boolean result = s.prepare(context);
                    logger.info("Service {} prepare returned {}", s.getClass().getSimpleName(), result);
                    return result;
                } catch (Exception e) {
                    logger.error("Service {} prepare threw exception: {}", s.getClass().getSimpleName(), e.getMessage());
                    return false;
                }
            });
            futures.add(future);
        }

        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(PREPARE_TIMEOUT_SECONDS, TimeUnit.SECONDS);
                if (!result) {
                    allPrepared = false;
                }
            } catch (TimeoutException te) {
                logger.error("Service prepare timed out after {} seconds", PREPARE_TIMEOUT_SECONDS);
                allPrepared = false;
            } catch (Exception e) {
                logger.error("Exception during prepare phase: {}", e.getMessage());
                allPrepared = false;
            }
        }

        if (!allPrepared) {
            logger.warn("Prepare phase failed for transaction: {}. Initiating rollback.", context.getTransactionId());
            rollback(services, context);
            throw new RuntimeException("Prepare phase failed. Transaction rolled back.");
        }

        logger.info("All services prepared successfully for transaction: {}. Starting commit phase.", context.getTransactionId());
        for (Service s : services) {
            executeWithRetry(() -> {
                s.commit(context);
                logger.info("Service {} commit successful.", s.getClass().getSimpleName());
                return null;
            });
        }
        logger.info("Transaction {} committed successfully.", context.getTransactionId());
    }

    public void rollback(List<Service> services, TransactionContext context) {
        logger.info("Starting rollback for transaction: {}", context.getTransactionId());
        for (Service s : services) {
            try {
                executeWithRetry(() -> {
                    s.rollback(context);
                    logger.info("Service {} rollback successful.", s.getClass().getSimpleName());
                    return null;
                });
            } catch (Exception e) {
                logger.error("Service {} rollback ultimately failed: {}", s.getClass().getSimpleName(), e.getMessage());
            }
        }
        logger.info("Rollback completed for transaction: {}", context.getTransactionId());
    }

    private <T> T executeWithRetry(Callable<T> callable) {
        long backoff = INITIAL_BACKOFF_MILLIS;
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                return callable.call();
            } catch (Exception e) {
                logger.warn("Attempt {} failed with exception: {}. Retrying after {} ms", attempt + 1, e.getMessage(), backoff);
                try {
                    Thread.sleep(backoff);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Interrupted during retry backoff", ie);
                }
                backoff *= 2;
            }
        }
        try {
            return callable.call();
        } catch (Exception e) {
            logger.error("Operation failed after {} retries: {}", MAX_RETRIES, e.getMessage());
            throw new RuntimeException("Operation failed after retries", e);
        }
    }
}