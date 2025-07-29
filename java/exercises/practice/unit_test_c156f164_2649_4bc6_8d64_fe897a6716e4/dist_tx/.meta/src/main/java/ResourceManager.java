public interface ResourceManager {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}