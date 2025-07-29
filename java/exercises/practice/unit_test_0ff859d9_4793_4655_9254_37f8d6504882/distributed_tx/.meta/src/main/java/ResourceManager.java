public interface ResourceManager {
    boolean prepare(TransactionID transactionId);
    void commit(TransactionID transactionId);
    void rollback(TransactionID transactionId);
    TransactionState recover(TransactionID transactionId);
}