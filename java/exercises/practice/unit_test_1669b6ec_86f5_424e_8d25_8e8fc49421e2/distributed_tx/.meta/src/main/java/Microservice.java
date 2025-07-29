package distributed_tx;

public interface Microservice {
    boolean prepare(int transactionId);
    void commit(int transactionId);
    void rollback(int transactionId);
}