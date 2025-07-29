import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

/**
 * This class maintains a transaction log for tracking the state of
 * distributed transactions and enabling recovery scenarios.
 * In a production environment, this would be persisted to a durable store.
 */
public class TransactionLog {
    private static final Logger LOGGER = Logger.getLogger(TransactionLog.class.getName());
    
    public enum TransactionState {
        STARTED,
        PREPARING,
        INVENTORY_PREPARED,
        ORDER_PREPARED,
        COMMITTING,
        COMMITTED,
        ROLLING_BACK,
        ROLLED_BACK,
        FAILED
    }
    
    public static class TransactionRecord {
        private final String transactionId;
        private TransactionState state;
        private final Map<String, Object> metadata;
        
        public TransactionRecord(String transactionId) {
            this.transactionId = transactionId;
            this.state = TransactionState.STARTED;
            this.metadata = new HashMap<>();
        }
        
        public void setState(TransactionState state) {
            this.state = state;
        }
        
        public TransactionState getState() {
            return state;
        }
        
        public void addMetadata(String key, Object value) {
            metadata.put(key, value);
        }
        
        public Object getMetadata(String key) {
            return metadata.get(key);
        }
        
        @Override
        public String toString() {
            return "Transaction[id=" + transactionId + ", state=" + state + "]";
        }
    }
    
    private final Map<String, TransactionRecord> transactions = new ConcurrentHashMap<>();
    
    public TransactionRecord createTransaction(String transactionId) {
        TransactionRecord record = new TransactionRecord(transactionId);
        transactions.put(transactionId, record);
        LOGGER.info("Transaction created: " + record);
        return record;
    }
    
    public TransactionRecord getTransaction(String transactionId) {
        return transactions.get(transactionId);
    }
    
    public void updateTransactionState(String transactionId, TransactionState state) {
        TransactionRecord record = transactions.get(transactionId);
        if (record != null) {
            record.setState(state);
            LOGGER.info("Transaction updated: " + record);
        }
    }
    
    public void addTransactionMetadata(String transactionId, String key, Object value) {
        TransactionRecord record = transactions.get(transactionId);
        if (record != null) {
            record.addMetadata(key, value);
        }
    }
    
    // In a real implementation, this would include methods for:
    // - Persisting the log to a durable store
    // - Recovery from failure scenarios
    // - Cleanup of completed transactions after a certain time
}