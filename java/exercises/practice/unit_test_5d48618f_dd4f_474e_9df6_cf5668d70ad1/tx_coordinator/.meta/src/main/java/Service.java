public interface Service {
    boolean prepare(String transactionId);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}