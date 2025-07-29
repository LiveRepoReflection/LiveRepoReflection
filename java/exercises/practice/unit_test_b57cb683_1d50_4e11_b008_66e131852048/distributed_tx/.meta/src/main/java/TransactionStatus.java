package distributed_tx;

public enum TransactionStatus {
    IN_FLIGHT,
    COMMITTED,
    ABORTED
}