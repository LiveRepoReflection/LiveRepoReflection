import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.stream.Collectors;

/**
 * Implements a distributed transaction manager using the two-phase commit protocol.
 */
public class DistributedTransactionManager {
    private static final Logger LOGGER = Logger.getLogger(DistributedTransactionManager.class.getName());
    
    private final Shard[] shards;
    private final Map<String, TransactionState> transactions;
    private final Map<String, Lock> transactionLocks;
    private final Random random;
    
    /**
     * Constructs a new DistributedTransactionManager.
     * 
     * @param shards The array of shards to manage.
     */
    public DistributedTransactionManager(Shard[] shards) {
        this.shards = shards;
        this.transactions = new ConcurrentHashMap<>();
        this.transactionLocks = new ConcurrentHashMap<>();
        this.random = new Random();
    }
    
    /**
     * Begins a new transaction.
     * 
     * @return A unique transaction ID.
     */
    public String begin() {
        String transactionId = generateTransactionId();
        transactions.put(transactionId, new TransactionState());
        transactionLocks.put(transactionId, new ReentrantLock());
        LOGGER.info("Transaction " + transactionId + " started");
        return transactionId;
    }
    
    /**
     * Executes a list of operations in a transaction.
     * 
     * @param transactionId The ID of the transaction.
     * @param operations The operations to execute.
     * @return true if the operations were successfully prepared for execution, false otherwise.
     */
    public boolean execute(String transactionId, List<Operation> operations) {
        Lock lock = transactionLocks.get(transactionId);
        if (lock == null) {
            LOGGER.warning("Invalid transaction ID: " + transactionId);
            return false;
        }
        
        lock.lock();
        try {
            TransactionState state = transactions.get(transactionId);
            if (state == null || state.getState() != TransactionStatus.ACTIVE) {
                LOGGER.warning("Transaction " + transactionId + " is not active");
                return false;
            }
            
            // Group operations by shard for batching
            Map<Integer, List<Operation>> operationsByShardId = operations.stream()
                    .collect(Collectors.groupingBy(Operation::getShardId));
                    
            // Prepare phase - Implement the first phase of 2PC
            Map<Integer, Boolean> prepareResults = new HashMap<>();
            
            for (Map.Entry<Integer, List<Operation>> entry : operationsByShardId.entrySet()) {
                int shardId = entry.getKey();
                List<Operation> shardOps = entry.getValue();
                
                // Skip prepare phase for read-only shards
                boolean readOnly = shardOps.stream()
                        .allMatch(op -> op.getOperationType() == OperationType.READ);
                
                if (readOnly) {
                    // Execute reads directly and skip prepare
                    for (Operation op : shardOps) {
                        String result = shards[shardId].read(op.getKey());
                        state.addReadResult(op, result);
                    }
                    prepareResults.put(shardId, true);
                    state.markShardReadOnly(shardId);
                } else {
                    // Prepare the non-read-only shard
                    try {
                        boolean prepared = shards[shardId].prepare(transactionId, shardOps);
                        prepareResults.put(shardId, prepared);
                        if (!prepared) {
                            LOGGER.warning("Prepare failed for shard " + shardId + " in transaction " + transactionId);
                            break;
                        }
                    } catch (Exception e) {
                        LOGGER.log(Level.SEVERE, "Error during prepare for shard " + shardId, e);
                        prepareResults.put(shardId, false);
                        break;
                    }
                }
            }
            
            // Check if all shards are prepared
            boolean allPrepared = prepareResults.values().stream().allMatch(Boolean::booleanValue);
            
            if (allPrepared) {
                state.setState(TransactionStatus.PREPARED);
                state.setOperationsByShardId(operationsByShardId);
                LOGGER.info("Transaction " + transactionId + " prepared successfully");
                return true;
            } else {
                // Roll back any prepared shards if preparation fails
                rollbackPreparedShards(transactionId, prepareResults);
                state.setState(TransactionStatus.ABORTED);
                LOGGER.warning("Transaction " + transactionId + " preparation failed, rolled back");
                return false;
            }
        } finally {
            lock.unlock();
        }
    }
    
    /**
     * Commits a transaction.
     * 
     * @param transactionId The ID of the transaction to commit.
     * @return true if the transaction was successfully committed, false otherwise.
     */
    public boolean commit(String transactionId) {
        Lock lock = transactionLocks.get(transactionId);
        if (lock == null) {
            LOGGER.warning("Invalid transaction ID: " + transactionId);
            return false;
        }
        
        lock.lock();
        try {
            TransactionState state = transactions.get(transactionId);
            if (state == null || state.getState() != TransactionStatus.PREPARED) {
                LOGGER.warning("Transaction " + transactionId + " is not prepared for commit");
                return false;
            }
            
            // Commit phase - Implement the second phase of 2PC
            boolean allCommitted = true;
            List<Integer> committedShards = new ArrayList<>();
            
            Map<Integer, List<Operation>> operationsByShardId = state.getOperationsByShardId();
            for (Integer shardId : operationsByShardId.keySet()) {
                if (state.isShardReadOnly(shardId)) {
                    // Read-only shards don't need to be committed
                    continue;
                }
                
                try {
                    boolean committed = shards[shardId].commit(transactionId);
                    if (committed) {
                        committedShards.add(shardId);
                    } else {
                        allCommitted = false;
                        LOGGER.warning("Commit failed for shard " + shardId + " in transaction " + transactionId);
                        break;
                    }
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Error during commit for shard " + shardId, e);
                    allCommitted = false;
                    break;
                }
            }
            
            if (allCommitted) {
                state.setState(TransactionStatus.COMMITTED);
                LOGGER.info("Transaction " + transactionId + " committed successfully");
                return true;
            } else {
                // If commit fails, attempt to rollback where possible
                // Note: This is a best-effort recovery and may not succeed in all cases
                LOGGER.warning("Commit failed for transaction " + transactionId + ", attempting recovery");
                for (Integer shardId : committedShards) {
                    try {
                        shards[shardId].rollback(transactionId);
                    } catch (Exception e) {
                        LOGGER.log(Level.SEVERE, "Failed to rollback committed shard " + shardId, e);
                    }
                }
                state.setState(TransactionStatus.ABORTED);
                return false;
            }
        } finally {
            lock.unlock();
        }
    }
    
    /**
     * Rolls back a transaction.
     * 
     * @param transactionId The ID of the transaction to roll back.
     * @return true if the transaction was successfully rolled back, false otherwise.
     */
    public boolean rollback(String transactionId) {
        Lock lock = transactionLocks.get(transactionId);
        if (lock == null) {
            LOGGER.warning("Invalid transaction ID: " + transactionId);
            return false;
        }
        
        lock.lock();
        try {
            TransactionState state = transactions.get(transactionId);
            if (state == null) {
                LOGGER.warning("Transaction " + transactionId + " does not exist");
                return false;
            }
            
            // Can only rollback active or prepared transactions
            if (state.getState() != TransactionStatus.ACTIVE && state.getState() != TransactionStatus.PREPARED) {
                LOGGER.warning("Cannot rollback transaction " + transactionId + " in state " + state.getState());
                return false;
            }
            
            Map<Integer, List<Operation>> operationsByShardId = state.getOperationsByShardId();
            if (operationsByShardId != null) {
                for (Integer shardId : operationsByShardId.keySet()) {
                    if (!state.isShardReadOnly(shardId)) {
                        try {
                            shards[shardId].rollback(transactionId);
                        } catch (Exception e) {
                            LOGGER.log(Level.SEVERE, "Failed to rollback shard " + shardId, e);
                        }
                    }
                }
            }
            
            state.setState(TransactionStatus.ABORTED);
            LOGGER.info("Transaction " + transactionId + " rolled back");
            return true;
        } finally {
            lock.unlock();
        }
    }
    
    /**
     * Rolls back shards that were successfully prepared when the overall preparation fails.
     * 
     * @param transactionId The ID of the transaction.
     * @param prepareResults The map of shard IDs to preparation results.
     */
    private void rollbackPreparedShards(String transactionId, Map<Integer, Boolean> prepareResults) {
        TransactionState state = transactions.get(transactionId);
        
        for (Map.Entry<Integer, Boolean> entry : prepareResults.entrySet()) {
            int shardId = entry.getKey();
            boolean prepared = entry.getValue();
            
            if (prepared && !state.isShardReadOnly(shardId)) {
                try {
                    shards[shardId].rollback(transactionId);
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Failed to rollback shard " + shardId + " after prepare failure", e);
                }
            }
        }
    }
    
    /**
     * Generates a unique transaction ID.
     * 
     * @return A unique transaction ID.
     */
    private String generateTransactionId() {
        return "tx-" + UUID.randomUUID().toString();
    }
    
    /**
     * Represents the state of a transaction.
     */
    private static class TransactionState {
        private TransactionStatus state;
        private Map<Integer, List<Operation>> operationsByShardId;
        private final Map<String, String> readResults;
        private final Set<Integer> readOnlyShards;
        
        TransactionState() {
            this.state = TransactionStatus.ACTIVE;
            this.operationsByShardId = null;
            this.readResults = new HashMap<>();
            this.readOnlyShards = new HashSet<>();
        }
        
        void setState(TransactionStatus state) {
            this.state = state;
        }
        
        TransactionStatus getState() {
            return state;
        }
        
        void setOperationsByShardId(Map<Integer, List<Operation>> operationsByShardId) {
            this.operationsByShardId = operationsByShardId;
        }
        
        Map<Integer, List<Operation>> getOperationsByShardId() {
            return operationsByShardId;
        }
        
        void addReadResult(Operation operation, String result) {
            readResults.put(operation.getKey(), result);
        }
        
        String getReadResult(String key) {
            return readResults.get(key);
        }
        
        void markShardReadOnly(int shardId) {
            readOnlyShards.add(shardId);
        }
        
        boolean isShardReadOnly(int shardId) {
            return readOnlyShards.contains(shardId);
        }
    }
    
    /**
     * Enum representing the status of a transaction.
     */
    private enum TransactionStatus {
        ACTIVE,
        PREPARED,
        COMMITTED,
        ABORTED
    }
}