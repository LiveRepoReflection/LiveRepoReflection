package distributed_tx;

public interface Resource {
    boolean prepare(TransactionContext context) throws InterruptedException;
    boolean commit(TransactionContext context) throws InterruptedException;
    boolean rollback(TransactionContext context) throws InterruptedException;
}