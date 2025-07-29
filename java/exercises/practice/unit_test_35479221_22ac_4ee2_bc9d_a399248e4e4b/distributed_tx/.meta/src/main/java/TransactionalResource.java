package distributed_tx;

public interface TransactionalResource {
    boolean prepare();
    void commit();
    void rollback();
}