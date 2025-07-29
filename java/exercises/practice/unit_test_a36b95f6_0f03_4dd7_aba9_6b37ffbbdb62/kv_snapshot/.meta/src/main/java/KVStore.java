package kv_snapshot;

public interface KVStore {
    int beginTransaction();
    String get(int transactionId, String key) throws InvalidTransactionException;
    void put(int transactionId, String key, String value) throws InvalidTransactionException;
    void commitTransaction(int transactionId) throws TransactionConflictException, InvalidTransactionException;
    void abortTransaction(int transactionId) throws InvalidTransactionException;
}