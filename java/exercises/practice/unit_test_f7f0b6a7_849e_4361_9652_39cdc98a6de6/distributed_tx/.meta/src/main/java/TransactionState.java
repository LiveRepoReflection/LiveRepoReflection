public enum TransactionState {
    PENDING,
    PREPARING,
    PREPARED,
    COMMITTING,
    COMMITTED,
    ROLLING_BACK,
    ROLLED_BACK,
    ABORTED
}