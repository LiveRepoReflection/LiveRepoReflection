package distributed_tx;

import java.util.logging.Logger;

public class DistributedTransactionCoordinator {
    private static final Logger logger = Logger.getLogger(DistributedTransactionCoordinator.class.getName());
    
    private final ServiceEndpoint serviceA;
    private final ServiceEndpoint serviceB;
    private final int maxRetries;
    private final int prepareTimeout; // in milliseconds

    public DistributedTransactionCoordinator(ServiceEndpoint serviceA, ServiceEndpoint serviceB) {
        // Default maximum retries = 3 and prepare timeout = 1000ms
        this(serviceA, serviceB, 3, 1000);
    }
    
    public DistributedTransactionCoordinator(ServiceEndpoint serviceA, ServiceEndpoint serviceB, int maxRetries, int prepareTimeout) {
        this.serviceA = serviceA;
        this.serviceB = serviceB;
        this.maxRetries = maxRetries;
        this.prepareTimeout = prepareTimeout;
    }
    
    public String processTransaction(TransactionRequest request) {
        logger.info("Starting transaction: " + request.transactionId);
        boolean aPrepared = false;
        boolean bPrepared = false;
        long startTime;
        
        // Prepare phase for Service A
        startTime = System.currentTimeMillis();
        aPrepared = serviceA.prepare(request.transactionId, request.serviceAAccountId, request.amount, request.serviceAExpectedVersion);
        if (System.currentTimeMillis() - startTime > prepareTimeout) {
            logger.warning("Prepare phase timeout for Service A on transaction: " + request.transactionId);
            aPrepared = false;
        }
        
        // Prepare phase for Service B
        startTime = System.currentTimeMillis();
        bPrepared = serviceB.prepare(request.transactionId, request.serviceBAccountId, request.amount, request.serviceBExpectedVersion);
        if (System.currentTimeMillis() - startTime > prepareTimeout) {
            logger.warning("Prepare phase timeout for Service B on transaction: " + request.transactionId);
            bPrepared = false;
        }
        
        if (aPrepared && bPrepared) {
            logger.info("Prepare phase successful for transaction: " + request.transactionId);
            boolean aCommitted = retryCommit(serviceA, request.transactionId);
            boolean bCommitted = retryCommit(serviceB, request.transactionId);
            
            if (aCommitted && bCommitted) {
                logger.info("Commit phase successful for transaction: " + request.transactionId);
                return "SUCCESS";
            } else {
                logger.warning("Commit phase failure, initiating rollback for transaction: " + request.transactionId);
                retryRollback(serviceA, request.transactionId);
                retryRollback(serviceB, request.transactionId);
                return "FAILURE";
            }
        } else {
            logger.warning("Prepare phase failed, initiating rollback for transaction: " + request.transactionId);
            retryRollback(serviceA, request.transactionId);
            retryRollback(serviceB, request.transactionId);
            return "FAILURE";
        }
    }
    
    private boolean retryCommit(ServiceEndpoint service, String transactionId) {
        int attempts = 0;
        while (attempts < maxRetries) {
            if (service.commit(transactionId)) {
                return true;
            }
            attempts++;
            logger.info("Retrying commit for transaction: " + transactionId + ", attempt: " + (attempts + 1));
        }
        return false;
    }
    
    private boolean retryRollback(ServiceEndpoint service, String transactionId) {
        int attempts = 0;
        while (attempts < maxRetries) {
            if (service.rollback(transactionId)) {
                return true;
            }
            attempts++;
            logger.info("Retrying rollback for transaction: " + transactionId + ", attempt: " + (attempts + 1));
        }
        return false;
    }
}