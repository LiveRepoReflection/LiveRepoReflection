package distributed_tx;

public interface ServiceEndpoint {
    boolean prepare(String transactionId, String accountId, double amount, int expectedVersion);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}