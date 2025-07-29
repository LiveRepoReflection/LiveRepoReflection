public interface Participant {
    boolean prepare(Transaction transaction);
    void commit(Transaction transaction);
    void rollback(Transaction transaction);
}