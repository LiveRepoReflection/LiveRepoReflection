import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * A coordinator for managing distributed transactions across multiple service endpoints.
 * Implements the two-phase commit (2PC) protocol.
 */
public class TransactionCoordinator {
    private static final Logger LOGGER = Logger.getLogger(TransactionCoordinator.class.getName());
    
    // Configuration constants
    private static final int PREPARE_TIMEOUT_MS = 5000; // 5 seconds
    private static final int MAX_RETRIES = 3;
    private static final long RETRY_DELAY_MS = 1000; // 1 second
    
    // In-memory storage for transactions
    private final Map<String, Transaction> transactions = new ConcurrentHashMap<>();
    
    /**
     * Begins a new transaction with the specified ID.
     *
     * @param transactionId The unique identifier for the transaction
     * @return true if the transaction was successfully created, false if a transaction with the same ID already exists
     */
    public boolean beginTransaction(String transactionId) {
        LOGGER.log(Level.INFO, "Beginning transaction: {0}", transactionId);
        
        Transaction transaction = new Transaction(transactionId);
        Transaction existing = transactions.putIfAbsent(transactionId, transaction);
        
        if (existing != null) {
            LOGGER.log(Level.WARNING, "Transaction {0} already exists", transactionId);
            return false;
        }
        
        return true;
    }
    
    /**
     * Registers a service endpoint with the specified transaction.
     *
     * @param transactionId The ID of the transaction
     * @param serviceEndpoint The service endpoint to enlist
     * @return true if the service was successfully enlisted, false otherwise
     */
    public boolean enlistService(String transactionId, ServiceEndpoint serviceEndpoint) {
        LOGGER.log(Level.INFO, "Enlisting service in transaction: {0}", transactionId);
        
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            LOGGER.log(Level.WARNING, "Cannot enlist service: Transaction {0} does not exist", transactionId);
            return false;
        }
        
        return transaction.enlistService(serviceEndpoint);
    }
    
    /**
     * Initiates the "prepare" phase of the two-phase commit protocol.
     *
     * @param transactionId The ID of the transaction
     * @return The transaction status after the prepare phase
     */
    public TransactionStatus prepareTransaction(String transactionId) {
        LOGGER.log(Level.INFO, "Preparing transaction: {0}", transactionId);
        
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            LOGGER.log(Level.WARNING, "Cannot prepare: Transaction {0} does not exist", transactionId);
            return TransactionStatus.UNKNOWN;
        }
        
        return transaction.prepare();
    }
    
    /**
     * Commits the transaction.
     *
     * @param transactionId The ID of the transaction
     */
    public void commitTransaction(String transactionId) {
        LOGGER.log(Level.INFO, "Committing transaction: {0}", transactionId);
        
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            LOGGER.log(Level.WARNING, "Cannot commit: Transaction {0} does not exist", transactionId);
            return;
        }
        
        transaction.commit();
    }
    
    /**
     * Rolls back the transaction.
     *
     * @param transactionId The ID of the transaction
     */
    public void rollbackTransaction(String transactionId) {
        LOGGER.log(Level.INFO, "Rolling back transaction: {0}", transactionId);
        
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            LOGGER.log(Level.WARNING, "Cannot rollback: Transaction {0} does not exist", transactionId);
            return;
        }
        
        transaction.rollback();
    }
    
    /**
     * Gets the current status of a transaction.
     *
     * @param transactionId The ID of the transaction
     * @return The current status of the transaction
     */
    public TransactionStatus getTransactionStatus(String transactionId) {
        Transaction transaction = transactions.get(transactionId);
        if (transaction == null) {
            return TransactionStatus.UNKNOWN;
        }
        
        return transaction.getStatus();
    }
    
    /**
     * Internal class representing a transaction.
     */
    private class Transaction {
        private final String id;
        private final Set<ServiceEndpoint> enlistedServices = ConcurrentHashMap.newKeySet();
        private volatile TransactionStatus status = TransactionStatus.ACTIVE;
        
        public Transaction(String id) {
            this.id = id;
        }
        
        public boolean enlistService(ServiceEndpoint endpoint) {
            return enlistedServices.add(endpoint);
        }
        
        public TransactionStatus prepare() {
            if (status != TransactionStatus.ACTIVE) {
                LOGGER.log(Level.WARNING, "Cannot prepare transaction {0}: Invalid state {1}", new Object[]{id, status});
                return TransactionStatus.UNKNOWN;
            }
            
            status = TransactionStatus.PREPARING;
            
            if (enlistedServices.isEmpty()) {
                LOGGER.log(Level.INFO, "No services enlisted in transaction {0}, auto-committing", id);
                return TransactionStatus.COMMIT;
            }
            
            // Call prepare on all enlisted services
            boolean allCommitted = true;
            boolean anyRollback = false;
            
            for (ServiceEndpoint service : enlistedServices) {
                ServiceResponse response = prepareServiceWithRetry(service);
                
                if (response == ServiceResponse.ROLLBACK) {
                    anyRollback = true;
                    LOGGER.log(Level.INFO, "Service voted to roll back transaction {0}", id);
                    break;
                } else if (response == ServiceResponse.ERROR) {
                    LOGGER.log(Level.WARNING, "Service error during prepare of transaction {0}", id);
                    return TransactionStatus.UNKNOWN;
                }
            }
            
            if (anyRollback) {
                return TransactionStatus.ROLLBACK;
            } else if (allCommitted) {
                return TransactionStatus.COMMIT;
            } else {
                return TransactionStatus.UNKNOWN;
            }
        }
        
        private ServiceResponse prepareServiceWithRetry(ServiceEndpoint service) {
            for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
                try {
                    ServiceResponse response = callPrepareWithTimeout(service);
                    if (response != ServiceResponse.ERROR) {
                        return response;
                    }
                    
                    // If we got an error, we'll retry after a delay
                    LOGGER.log(Level.INFO, "Retrying prepare after error (attempt {0}/{1})", new Object[]{attempt + 1, MAX_RETRIES});
                    Thread.sleep(RETRY_DELAY_MS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    LOGGER.log(Level.WARNING, "Thread interrupted during prepare retry", e);
                    return ServiceResponse.ERROR;
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error during prepare", e);
                    return ServiceResponse.ERROR;
                }
            }
            
            LOGGER.log(Level.WARNING, "Failed to prepare service after {0} attempts", MAX_RETRIES);
            return ServiceResponse.ERROR;
        }
        
        private ServiceResponse callPrepareWithTimeout(ServiceEndpoint service) {
            // Create a worker thread to call prepare
            final ServiceResponse[] responseHolder = new ServiceResponse[1];
            Thread worker = new Thread(() -> {
                try {
                    responseHolder[0] = service.prepare();
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Exception in prepare call", e);
                    responseHolder[0] = ServiceResponse.ERROR;
                }
            });
            
            // Start the worker and wait for it to finish
            worker.start();
            try {
                worker.join(PREPARE_TIMEOUT_MS);
                
                if (worker.isAlive()) {
                    // Timeout occurred, interrupt the worker thread
                    worker.interrupt();
                    LOGGER.log(Level.WARNING, "Prepare call timed out after {0}ms", PREPARE_TIMEOUT_MS);
                    return ServiceResponse.ERROR;
                }
                
                return responseHolder[0] != null ? responseHolder[0] : ServiceResponse.ERROR;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                LOGGER.log(Level.WARNING, "Interrupted while waiting for prepare call", e);
                return ServiceResponse.ERROR;
            }
        }
        
        public void commit() {
            LOGGER.log(Level.INFO, "Committing transaction {0}", id);
            
            status = TransactionStatus.COMMITTING;
            
            for (ServiceEndpoint service : enlistedServices) {
                try {
                    service.commit();
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error committing service in transaction " + id, e);
                    // Continue with other services even if one fails
                }
            }
            
            status = TransactionStatus.COMMITTED;
        }
        
        public void rollback() {
            LOGGER.log(Level.INFO, "Rolling back transaction {0}", id);
            
            status = TransactionStatus.ROLLING_BACK;
            
            for (ServiceEndpoint service : enlistedServices) {
                try {
                    service.rollback();
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error rolling back service in transaction " + id, e);
                    // Continue with other services even if one fails
                }
            }
            
            status = TransactionStatus.ROLLED_BACK;
        }
        
        public TransactionStatus getStatus() {
            return status;
        }
    }
}