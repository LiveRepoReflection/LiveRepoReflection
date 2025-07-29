package distributed_tx;

public interface TransactionalService {
    boolean prepare(String transactionId) throws Exception;
    void commit(String transactionId) throws Exception;
    void rollback(String transactionId) throws Exception;
}