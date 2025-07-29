package tx_coordinator;

public interface Service {
    String getName();
    boolean prepare(String transactionId, String data);
    void commit(String transactionId);
    void rollback(String transactionId);
}