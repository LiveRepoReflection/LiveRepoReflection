package distributed_tx;

public interface Service {
    String getName();
    boolean prepare(TransactionContext transactionContext, String operation);
    boolean commit(TransactionContext transactionContext, String operation);
    boolean rollback(TransactionContext transactionContext, String operation);
}