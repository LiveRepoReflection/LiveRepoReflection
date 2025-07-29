public interface Service {
    String getName();
    boolean prepare(Transaction txn);
    void commit(Transaction txn);
    void rollback(Transaction txn);
}