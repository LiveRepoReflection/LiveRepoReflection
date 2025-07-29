public interface Service {
    boolean prepare(TransactionContext context);
    void commit(TransactionContext context);
    void rollback(TransactionContext context);
}