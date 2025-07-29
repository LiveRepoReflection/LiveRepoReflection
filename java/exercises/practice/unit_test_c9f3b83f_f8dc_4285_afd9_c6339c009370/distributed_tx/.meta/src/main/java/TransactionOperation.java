package distributed_tx;

public interface TransactionOperation {
    boolean prepare();
    void commit();
    void rollback();
    void execute();
}