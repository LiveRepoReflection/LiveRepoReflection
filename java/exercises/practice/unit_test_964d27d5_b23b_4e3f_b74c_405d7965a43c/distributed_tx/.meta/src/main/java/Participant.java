public interface Participant {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
}