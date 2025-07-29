package distributed_tx;

public interface Service {
    boolean prepare(TransactionContext tx);
    void commit(TransactionContext tx);
    void rollback(TransactionContext tx);
}