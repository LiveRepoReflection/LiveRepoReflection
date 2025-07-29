package tx_coordinator;

public enum TransactionStatus {
    BEGIN,
    PREPARING,
    COMMIT_PENDING,
    ROLLBACK_PENDING,
    COMMITTED,
    ROLLED_BACK
}