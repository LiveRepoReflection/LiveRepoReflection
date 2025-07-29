import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * A transaction manager that orchestrates distributed transactions across multiple services.
 * Implements a simplified two-phase commit protocol for distributed transaction management.
 */
public class TransactionManager {
    private static final Logger LOGGER = Logger.getLogger(TransactionManager.class.getName());
    
    // Generate unique transaction IDs
    private final AtomicLong nextTransactionId = new AtomicLong(1);
    
    // Track active transactions and their operations
    private final Map<Long, Transaction> activeTransactions = new ConcurrentHashMap<>();
    
    // Track transaction state to ensure idempotent rollbacks
    private final Map<Long, TransactionState> transactionStates = new ConcurrentHashMap<>();

    /**
     * Begins a new transaction and returns its unique identifier.
     * 
     * @return the unique ID for the new transaction
     */
    public long beginTransaction() {
        long txId = nextTransactionId.getAndIncrement();
        activeTransactions.put(txId, new Transaction());
        transactionStates.put(txId, TransactionState.ACTIVE);
        LOGGER.fine("Transaction " + txId + " started");
        return txId;
    }
    
    /**
     * Registers an operation to be performed as part of a transaction.
     * 
     * @param txId the transaction ID
     * @param serviceId the service ID that will execute the operation
     * @param operation the operation to execute
     * @param rollbackOperation the operation to execute to rollback changes if needed
     * @throws IllegalArgumentException if the transaction ID is invalid
     */
    public void registerOperation(long txId, int serviceId, 
                                 Callable<Boolean> operation, 
                                 Callable<Boolean> rollbackOperation) {
        Transaction tx = activeTransactions.get(txId);
        if (tx == null || transactionStates.get(txId) != TransactionState.ACTIVE) {
            throw new IllegalArgumentException("Invalid transaction ID: " + txId);
        }
        
        tx.addOperation(serviceId, operation, rollbackOperation);
        LOGGER.fine("Operation registered for transaction " + txId + " on service " + serviceId);
    }
    
    /**
     * Attempts to commit a transaction by executing all registered operations.
     * If any operation fails, rolls back the transaction.
     * 
     * @param txId the transaction ID
     * @return true if the transaction was successfully committed, false otherwise
     * @throws IllegalArgumentException if the transaction ID is invalid
     */
    public boolean commitTransaction(long txId) {
        Transaction tx = activeTransactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Invalid transaction ID: " + txId);
        }
        
        TransactionState state = transactionStates.get(txId);
        if (state != TransactionState.ACTIVE) {
            LOGGER.warning("Attempted to commit transaction " + txId + " with state " + state);
            return state == TransactionState.COMMITTED;
        }
        
        LOGGER.fine("Attempting to commit transaction " + txId);
        
        // First phase: Prepare (execute operations but keep changes local)
        Map<Integer, OperationResult> results = tx.executeOperations();
        
        // Check if all operations succeeded
        boolean allSucceeded = results.values().stream()
                .allMatch(result -> result.success && !result.hasException);
        
        if (allSucceeded) {
            // All operations succeeded, commit the transaction
            transactionStates.put(txId, TransactionState.COMMITTED);
            LOGGER.fine("Transaction " + txId + " committed successfully");
            return true;
        } else {
            // Some operations failed, rollback the transaction
            LOGGER.fine("Transaction " + txId + " failed, rolling back");
            rollbackTransaction(txId);
            return false;
        }
    }
    
    /**
     * Rolls back a transaction by executing all rollback operations.
     * 
     * @param txId the transaction ID
     * @throws IllegalArgumentException if the transaction ID is invalid
     */
    public void rollbackTransaction(long txId) {
        Transaction tx = activeTransactions.get(txId);
        if (tx == null) {
            throw new IllegalArgumentException("Invalid transaction ID: " + txId);
        }
        
        TransactionState state = transactionStates.get(txId);
        if (state == TransactionState.ROLLED_BACK) {
            // Already rolled back, maintain idempotency
            return;
        }
        
        LOGGER.fine("Rolling back transaction " + txId);
        tx.executeRollbacks();
        transactionStates.put(txId, TransactionState.ROLLED_BACK);
        LOGGER.fine("Transaction " + txId + " rolled back");
    }
    
    /**
     * Represents the state of a transaction.
     */
    private enum TransactionState {
        ACTIVE, COMMITTED, ROLLED_BACK
    }
    
    /**
     * Represents a transaction with its operations and rollback operations.
     */
    private static class Transaction {
        private final Map<Integer, OperationEntry> operations = new ConcurrentHashMap<>();
        private final Set<Integer> executedServices = ConcurrentHashMap.newKeySet();
        
        /**
         * Adds an operation to the transaction.
         */
        public void addOperation(int serviceId, Callable<Boolean> operation, Callable<Boolean> rollbackOperation) {
            operations.put(serviceId, new OperationEntry(operation, rollbackOperation));
        }
        
        /**
         * Executes all operations in the transaction.
         * 
         * @return a map of service IDs to operation results
         */
        public Map<Integer, OperationResult> executeOperations() {
            Map<Integer, OperationResult> results = new ConcurrentHashMap<>();
            
            for (Map.Entry<Integer, OperationEntry> entry : operations.entrySet()) {
                int serviceId = entry.getKey();
                OperationEntry opEntry = entry.getValue();
                
                try {
                    boolean success = opEntry.operation.call();
                    results.put(serviceId, new OperationResult(success, null));
                    
                    if (success) {
                        executedServices.add(serviceId);
                    } else {
                        // Operation returned false, no need to continue
                        break;
                    }
                } catch (Exception e) {
                    LOGGER.log(Level.WARNING, "Exception during operation execution on service " + serviceId, e);
                    results.put(serviceId, new OperationResult(false, e));
                    break;
                }
            }
            
            return results;
        }
        
        /**
         * Executes all rollback operations for services that had operations executed.
         */
        public void executeRollbacks() {
            // Only rollback services that had operations executed
            for (Integer serviceId : executedServices) {
                OperationEntry opEntry = operations.get(serviceId);
                if (opEntry != null) {
                    try {
                        opEntry.rollbackOperation.call();
                    } catch (Exception e) {
                        LOGGER.log(Level.SEVERE, "Exception during rollback on service " + serviceId, e);
                        // Continue with other rollbacks even if this one failed
                    }
                }
            }
            
            // Clear executed services after rollback
            executedServices.clear();
        }
    }
    
    /**
     * Represents an operation and its corresponding rollback operation.
     */
    private static class OperationEntry {
        public final Callable<Boolean> operation;
        public final Callable<Boolean> rollbackOperation;
        
        public OperationEntry(Callable<Boolean> operation, Callable<Boolean> rollbackOperation) {
            this.operation = operation;
            this.rollbackOperation = rollbackOperation;
        }
    }
    
    /**
     * Represents the result of an operation execution.
     */
    private static class OperationResult {
        public final boolean success;
        public final Exception exception;
        public final boolean hasException;
        
        public OperationResult(boolean success, Exception exception) {
            this.success = success;
            this.exception = exception;
            this.hasException = (exception != null);
        }
    }
}