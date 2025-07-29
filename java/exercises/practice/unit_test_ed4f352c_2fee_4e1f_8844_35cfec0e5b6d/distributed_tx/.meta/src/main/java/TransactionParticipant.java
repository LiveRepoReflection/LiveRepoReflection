public interface TransactionParticipant {
    boolean prepare() throws Exception;
    void commit();
    void rollback();
}