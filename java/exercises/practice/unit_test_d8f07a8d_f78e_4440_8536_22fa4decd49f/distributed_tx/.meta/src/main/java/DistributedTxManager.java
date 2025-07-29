import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * A distributed transaction manager that implements the Two-Phase Commit (2PC) protocol.
 * This manager coordinates transactions across multiple services.
 */
public class DistributedTxManager {

    private static final Logger LOGGER = Logger.getLogger(DistributedTxManager.class.getName());

    // Constants for timeouts and retry logic
    private static final int PREPARE_TIMEOUT_SECONDS = 5;
    private static final int COMMIT_TIMEOUT_SECONDS = 5;
    private static final int MAX_RETRIES = 3;
    private static final int RETRY_DELAY_MS = 500;

    // Map of registered services
    private final Map<String, TransactionParticipant> registeredServices;
    
    // Map of active transactions
    private final Map<String, TransactionContext> activeTransactions;
    
    // Locks for concurrency control
    private final Map<String, ReadWriteLock> serviceLocks;
    
    // Executor service for parallel processing
    private final ExecutorService executor;

    /**
     * Constructs a new DistributedTxManager.
     */
    public DistributedTxManager() {
        this.registeredServices = new ConcurrentHashMap<>();
        this.activeTransactions = new ConcurrentHashMap<>();
        this.serviceLocks = new ConcurrentHashMap<>();
        this.executor = Executors.newCachedThreadPool();
    }

    /**
     * Registers a service with the transaction manager.
     * 
     * @param serviceId The unique identifier for the service
     * @param service The service implementation
     */
    public void registerService(String serviceId, TransactionParticipant service) {
        if (serviceId == null || serviceId.isEmpty()) {
            throw new IllegalArgumentException("Service ID cannot be null or empty");
        }
        if (service == null) {
            throw new IllegalArgumentException("Service cannot be null");
        }
        
        registeredServices.put(serviceId, service);
        serviceLocks.put(serviceId, new ReentrantReadWriteLock());
        LOGGER.info("Registered service: " + serviceId);
    }

    /**
     * Begins a new transaction.
     * 
     * @param data Map of service IDs to the data they should process
     * @return Transaction ID
     * @throws IllegalArgumentException if any service ID is not registered
     */
    public String beginTransaction(Map<String, Object> data) {
        // Validate all service IDs exist
        for (String serviceId : data.keySet()) {
            if (!registeredServices.containsKey(serviceId)) {
                throw new IllegalArgumentException("Unknown service ID: " + serviceId);
            }
        }

        String txId = generateTransactionId();
        TransactionContext context = new TransactionContext(txId, data);
        activeTransactions.put(txId, context);
        
        LOGGER.info("Started transaction: " + txId + " with " + data.size() + " services");
        return txId;
    }

    /**
     * Executes a transaction using the Two-Phase Commit protocol.
     * 
     * @param txId The transaction ID
     * @return true if the transaction completed successfully, false otherwise
     */
    public boolean executeTransaction(String txId) {
        TransactionContext context = activeTransactions.get(txId);
        if (context == null) {
            throw new IllegalArgumentException("Unknown transaction ID: " + txId);
        }

        try {
            // Phase 1: Prepare
            boolean prepareSuccess = preparePhase(context);
            
            // Phase 2: Commit or Rollback
            if (prepareSuccess) {
                commitPhase(context);
                LOGGER.info("Transaction " + txId + " committed successfully");
                return true;
            } else {
                rollbackPhase(context);
                LOGGER.warning("Transaction " + txId + " rolled back after prepare failure");
                return false;
            }
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Transaction " + txId + " failed with exception", e);
            rollbackPhase(context);
            return false;
        } finally {
            activeTransactions.remove(txId);
        }
    }

    /**
     * Phase 1 of the Two-Phase Commit protocol: Prepare.
     * 
     * @param context The transaction context
     * @return true if all services prepared successfully, false otherwise
     */
    private boolean preparePhase(TransactionContext context) {
        Map<String, Object> data = context.getData();
        Map<String, Future<Boolean>> prepareFutures = new ConcurrentHashMap<>();
        
        // Submit prepare tasks in parallel
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            String serviceId = entry.getKey();
            Object serviceData = entry.getValue();
            
            prepareFutures.put(serviceId, executor.submit(() -> 
                prepareServiceWithRetry(serviceId, context.getTransactionId(), serviceData)));
        }
        
        // Wait for all prepare operations to complete
        for (Map.Entry<String, Future<Boolean>> entry : prepareFutures.entrySet()) {
            try {
                if (!entry.getValue().get(PREPARE_TIMEOUT_SECONDS, TimeUnit.SECONDS)) {
                    LOGGER.warning("Prepare failed for service " + entry.getKey() + 
                            " in transaction " + context.getTransactionId());
                    return false;
                }
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Exception during prepare phase for service " + entry.getKey(), e);
                return false;
            }
        }
        
        return true;
    }

    /**
     * Attempts to prepare a service with retry logic.
     * 
     * @param serviceId The service ID
     * @param txId The transaction ID
     * @param data The service-specific data
     * @return true if preparation succeeded, false otherwise
     */
    private boolean prepareServiceWithRetry(String serviceId, String txId, Object data) {
        TransactionParticipant service = registeredServices.get(serviceId);
        ReadWriteLock lock = serviceLocks.get(serviceId);
        
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                // Use read lock for prepare phase
                lock.readLock().lock();
                try {
                    boolean success = service.prepare(txId, data);
                    if (success) {
                        return true;
                    }
                    // If failed but not due to an exception, wait before retrying
                    Thread.sleep(RETRY_DELAY_MS);
                } finally {
                    lock.readLock().unlock();
                }
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Error preparing service " + serviceId + 
                        ", attempt " + (attempt + 1) + "/" + MAX_RETRIES, e);
                try {
                    Thread.sleep(RETRY_DELAY_MS);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }
        }
        
        return false;
    }

    /**
     * Phase 2 of the Two-Phase Commit protocol: Commit.
     * 
     * @param context The transaction context
     */
    private void commitPhase(TransactionContext context) {
        Map<String, Object> data = context.getData();
        Map<String, Future<?>> commitFutures = new ConcurrentHashMap<>();
        
        // Submit commit tasks in parallel
        for (String serviceId : data.keySet()) {
            commitFutures.put(serviceId, executor.submit(() -> 
                commitServiceWithRetry(serviceId, context.getTransactionId())));
        }
        
        // Wait for all commit operations to complete
        for (Map.Entry<String, Future<?>> entry : commitFutures.entrySet()) {
            try {
                entry.getValue().get(COMMIT_TIMEOUT_SECONDS, TimeUnit.SECONDS);
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, "Error during commit for service " + entry.getKey(), e);
                // We don't roll back here as it's too late - the transaction is considered committed
            }
        }
    }

    /**
     * Attempts to commit a service with retry logic.
     * 
     * @param serviceId The service ID
     * @param txId The transaction ID
     */
    private void commitServiceWithRetry(String serviceId, String txId) {
        TransactionParticipant service = registeredServices.get(serviceId);
        ReadWriteLock lock = serviceLocks.get(serviceId);
        
        for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                // Use write lock for commit phase
                lock.writeLock().lock();
                try {
                    service.commit(txId);
                    return;
                } finally {
                    lock.writeLock().unlock();
                }
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Error committing service " + serviceId + 
                        ", attempt " + (attempt + 1) + "/" + MAX_RETRIES, e);
                try {
                    Thread.sleep(RETRY_DELAY_MS);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
        
        LOGGER.severe("Failed to commit service " + serviceId + " after " + MAX_RETRIES + " attempts");
    }

    /**
     * Rolls back a transaction that failed during the prepare or commit phase.
     * 
     * @param context The transaction context
     */
    private void rollbackPhase(TransactionContext context) {
        Map<String, Object> data = context.getData();
        
        // Submit rollback tasks in parallel
        for (String serviceId : data.keySet()) {
            executor.execute(() -> {
                try {
                    TransactionParticipant service = registeredServices.get(serviceId);
                    ReadWriteLock lock = serviceLocks.get(serviceId);
                    
                    // Use write lock for rollback phase
                    lock.writeLock().lock();
                    try {
                        service.rollback(context.getTransactionId());
                    } finally {
                        lock.writeLock().unlock();
                    }
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Error rolling back service " + serviceId, e);
                }
            });
        }
    }

    /**
     * Generates a unique transaction ID.
     * 
     * @return A new unique transaction ID
     */
    private String generateTransactionId() {
        return "tx-" + UUID.randomUUID().toString();
    }

    /**
     * Cleans up resources when the manager is no longer needed.
     */
    public void shutdown() {
        try {
            executor.shutdown();
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Inner class to represent the context of a transaction.
     */
    private static class TransactionContext {
        private final String transactionId;
        private final Map<String, Object> data;
        
        public TransactionContext(String transactionId, Map<String, Object> data) {
            this.transactionId = transactionId;
            this.data = new ConcurrentHashMap<>(data);
        }
        
        public String getTransactionId() {
            return transactionId;
        }
        
        public Map<String, Object> getData() {
            return data;
        }
    }
}