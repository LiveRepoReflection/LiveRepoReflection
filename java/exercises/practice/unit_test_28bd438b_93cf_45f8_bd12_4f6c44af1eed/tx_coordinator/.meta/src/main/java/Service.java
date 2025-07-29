package tx_coordinator;

public interface Service {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}