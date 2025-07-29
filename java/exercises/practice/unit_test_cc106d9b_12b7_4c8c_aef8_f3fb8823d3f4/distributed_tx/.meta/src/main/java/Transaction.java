import java.util.UUID;

public class Transaction {
    private final String id;
    private final long timestamp;
    private TransactionState state;

    public Transaction(String id) {
        this.id = id;
        this.timestamp = System.currentTimeMillis();
        this.state = TransactionState.INITIATED;
    }

    public String getId() {
        return id;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public TransactionState getState() {
        return state;
    }

    public void setState(TransactionState state) {
        this.state = state;
    }
}