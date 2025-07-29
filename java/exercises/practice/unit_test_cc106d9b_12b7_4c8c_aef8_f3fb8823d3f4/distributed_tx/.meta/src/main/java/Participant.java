public interface Participant {
    Vote prepare(Transaction transaction) throws Exception;
    void commit(Transaction transaction) throws Exception;
    void rollback(Transaction transaction) throws Exception;
}