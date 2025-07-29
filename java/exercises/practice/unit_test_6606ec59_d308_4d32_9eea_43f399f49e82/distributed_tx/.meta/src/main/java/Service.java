package distributed_tx;

public interface Service {
    boolean prepare(String transactionId, Operation op) throws Exception;
    void commit(String transactionId) throws Exception;
    void rollback(String transactionId) throws Exception;
    String getName();
}