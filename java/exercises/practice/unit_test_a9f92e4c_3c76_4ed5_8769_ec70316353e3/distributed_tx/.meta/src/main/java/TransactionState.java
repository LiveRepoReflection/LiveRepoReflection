import java.io.Serializable;

public enum TransactionState implements Serializable {
    INITIATED,
    PREPARED,
    COMMITTED,
    ABORTED
}