import java.io.*;
import java.time.Instant;
import java.util.concurrent.ConcurrentHashMap;

public class TransactionLog implements Serializable {
    private static final ConcurrentHashMap<String, TransactionLog> logStore = new ConcurrentHashMap<>();
    
    private final String transactionId;
    private final Instant timestamp;
    private TransactionState state;

    public TransactionLog(String transactionId, TransactionState state) {
        this.transactionId = transactionId;
        this.timestamp = Instant.now();
        this.state = state;
    }

    public void persist() {
        logStore.put(transactionId, this);
    }

    public static TransactionLog load(String transactionId) {
        return logStore.get(transactionId);
    }

    public void updateState(TransactionState newState) {
        this.state = newState;
        persist();
    }

    public String getTransactionId() {
        return transactionId;
    }

    public Instant getTimestamp() {
        return timestamp;
    }

    public TransactionState getState() {
        return state;
    }
}