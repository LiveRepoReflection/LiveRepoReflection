package distributed_tx;

public interface Participant {
    boolean prepare(String transactionId) throws InterruptedException;
    void commit(String transactionId);
    void rollback(String transactionId);
}