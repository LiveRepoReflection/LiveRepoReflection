import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

public class DistributedTransactionManager {
    private static final Logger logger = Logger.getLogger(DistributedTransactionManager.class.getName());
    private final int maxRetries;
    private final long baseBackoffMillis;

    public DistributedTransactionManager() {
        // Default configuration: 3 retries with 100ms base backoff.
        this.maxRetries = 3;
        this.baseBackoffMillis = 100;
    }

    public DistributedTransactionManager(int maxRetries, long baseBackoffMillis) {
        this.maxRetries = maxRetries;
        this.baseBackoffMillis = baseBackoffMillis;
    }

    public boolean executeTransaction(List<Microservice> services, String transactionId) {
        logger.info("Starting transaction: " + transactionId);
        // Phase 1: Prepare all services
        for (Microservice service : services) {
            boolean prepared = false;
            try {
                prepared = service.prepare(transactionId);
                logger.info("Service " + service + " prepared transaction " + transactionId + " with outcome: " + prepared);
            } catch (Exception e) {
                logger.log(Level.WARNING, "Exception during prepare in service " + service + " for transaction " + transactionId, e);
            }
            if (!prepared) {
                logger.warning("Prepare phase failed for transaction " + transactionId + ". Initiating rollback.");
                rollbackAll(services, transactionId);
                return false;
            }
        }
        // Phase 2: Commit phase.
        logger.info("All services prepared successfully for transaction " + transactionId + ". Initiating commit.");
        boolean commitResult = commitAll(services, transactionId);
        if (!commitResult) {
            logger.warning("Commit phase failed for transaction " + transactionId + ". Initiating rollback.");
            rollbackAll(services, transactionId);
            return false;
        }
        logger.info("Transaction " + transactionId + " committed successfully.");
        return true;
    }

    private boolean commitAll(List<Microservice> services, String transactionId) {
        boolean allCommitted = true;
        for (Microservice service : services) {
            boolean committed = false;
            long backoff = baseBackoffMillis;
            for (int attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    service.commit(transactionId);
                    logger.info("Service " + service + " committed transaction " + transactionId + " at attempt " + attempt);
                    committed = true;
                    break;
                } catch (Exception e) {
                    logger.log(Level.WARNING, "Commit failed for service " + service + " on transaction " + transactionId + " at attempt " + attempt, e);
                    try {
                        Thread.sleep(backoff);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                    backoff *= 2;
                }
            }
            if (!committed) {
                logger.severe("Service " + service + " failed to commit transaction " + transactionId + " after " + maxRetries + " retries.");
                allCommitted = false;
            }
        }
        return allCommitted;
    }

    private void rollbackAll(List<Microservice> services, String transactionId) {
        for (Microservice service : services) {
            long backoff = baseBackoffMillis;
            for (int attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    service.rollback(transactionId);
                    logger.info("Service " + service + " rolled back transaction " + transactionId + " at attempt " + attempt);
                    break;
                } catch (Exception e) {
                    logger.log(Level.WARNING, "Rollback failed for service " + service + " on transaction " + transactionId + " at attempt " + attempt, e);
                    try {
                        Thread.sleep(backoff);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                    }
                    backoff *= 2;
                }
            }
        }
    }
}