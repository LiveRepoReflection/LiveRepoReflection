package distributed_tx;

public interface Branch {
    boolean prepare(String transactionId, Operation op);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}