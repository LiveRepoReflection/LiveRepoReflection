import java.io.Serializable;
import java.util.UUID;

public class TransactionContext implements Serializable {
    private final UUID transactionId;
    private Object data;

    public TransactionContext(UUID transactionId) {
        this.transactionId = transactionId;
    }

    public UUID getTransactionId() {
        return transactionId;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}