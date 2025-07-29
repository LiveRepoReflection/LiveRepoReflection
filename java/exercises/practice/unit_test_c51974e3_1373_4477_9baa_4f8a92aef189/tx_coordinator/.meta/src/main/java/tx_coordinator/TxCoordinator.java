package tx_coordinator;

import java.util.UUID;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeoutException;
import java.util.logging.Logger;
import java.util.logging.Level;

public class TxCoordinator {

    private final ConcurrentMap<UUID, List<Service>> transactions = new ConcurrentHashMap<>();
    private final ScheduledExecutorService executor = Executors.newScheduledThreadPool(4);
    private final int maxRetries = 3;
    private final int retryDelayMs = 100;
    private static final Logger logger = Logger.getLogger(TxCoordinator.class.getName());

    public TxCoordinator() {
        // Default constructor
    }

    public UUID begin() {
        UUID txId = UUID.randomUUID();
        transactions.put(txId, new CopyOnWriteArrayList<>());
        logger.info("Transaction begun: " + txId);
        return txId;
    }

    public void enlist(UUID transactionId, Service service) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList != null) {
            serviceList.add(service);
            logger.info("Service enlisted in transaction " + transactionId);
        } else {
            throw new IllegalArgumentException("Transaction does not exist: " + transactionId);
        }
    }

    public boolean commit(UUID transactionId) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList == null) {
            throw new IllegalArgumentException("Transaction does not exist: " + transactionId);
        }
        logger.info("Commit initiated for transaction " + transactionId);

        // Phase 1: Prepare phase
        for (Service service : serviceList) {
            try {
                logger.info("Calling prepare on service for transaction " + transactionId);
                boolean prepared = service.prepare(transactionId);
                if (!prepared) {
                    logger.warning("Prepare returned false, rolling back transaction " + transactionId);
                    rollback(transactionId);
                    transactions.remove(transactionId);
                    return false;
                }
            } catch (Exception e) {
                logger.log(Level.WARNING, "Exception in prepare: " + e.getMessage() + ", rolling back transaction " + transactionId, e);
                rollback(transactionId);
                transactions.remove(transactionId);
                return false;
            }
        }

        // Phase 2: Commit phase with retries
        for (Service service : serviceList) {
            boolean committed = executeWithRetry(() -> {
                service.commit(transactionId);
                return true;
            });
            if (!committed) {
                logger.warning("Commit failed on service, rolling back transaction " + transactionId);
                rollback(transactionId);
                transactions.remove(transactionId);
                return false;
            }
            logger.info("Commit succeeded on service for transaction " + transactionId);
        }
        transactions.remove(transactionId);
        logger.info("Transaction committed successfully: " + transactionId);
        return true;
    }

    public void rollback(UUID transactionId) {
        List<Service> serviceList = transactions.get(transactionId);
        if (serviceList == null) {
            throw new IllegalArgumentException("Transaction does not exist: " + transactionId);
        }
        logger.info("Rollback initiated for transaction " + transactionId);
        for (Service service : serviceList) {
            executeWithRetry(() -> {
                service.rollback(transactionId);
                return true;
            });
        }
        transactions.remove(transactionId);
        logger.info("Rollback completed for transaction " + transactionId);
    }

    private boolean executeWithRetry(Callable<Boolean> operation) {
        int attempts = 0;
        while (attempts < maxRetries) {
            try {
                return operation.call();
            } catch (TimeoutException e) {
                attempts++;
                logger.warning("TimeoutException encountered on attempt " + attempts + ": " + e.getMessage());
                sleepQuietly(retryDelayMs);
            } catch (Exception e) {
                // Check for service unavailable exception pattern or any exception retriable
                if(e.getMessage() != null && e.getMessage().contains("ServiceUnavailable")) {
                    attempts++;
                    logger.warning("ServiceUnavailableException encountered on attempt " + attempts + ": " + e.getMessage());
                    sleepQuietly(retryDelayMs);
                } else {
                    logger.log(Level.SEVERE, "Non-retryable exception encountered: " + e.getMessage(), e);
                    return false;
                }
            }
        }
        logger.severe("Operation failed after " + maxRetries + " attempts.");
        return false;
    }

    private void sleepQuietly(int millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
        }
    }
}