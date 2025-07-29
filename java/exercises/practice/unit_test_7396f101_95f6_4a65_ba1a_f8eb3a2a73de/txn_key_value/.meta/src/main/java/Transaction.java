import java.util.HashMap;
import java.util.Map;

/**
 * Represents a transaction in the distributed key-value store.
 */
public class Transaction {
    public final long timestamp;
    public final Map<String, String> writeset = new HashMap<>();
    
    // Maps node index to the writes that should be applied on that node
    public final Map<Integer, Map<String, String>> nodeWrites = new HashMap<>();
    
    public TransactionState state = TransactionState.ACTIVE;
    public final long startTimeMs = System.currentTimeMillis();

    public Transaction(long timestamp) {
        this.timestamp = timestamp;
    }
}