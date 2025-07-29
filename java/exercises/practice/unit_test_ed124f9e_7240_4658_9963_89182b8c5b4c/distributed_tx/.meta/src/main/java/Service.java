public interface Service {
    boolean prepare(String transactionId, String operation) throws Exception;
    void commit(String transactionId) throws Exception;
    void rollback(String transactionId) throws Exception;
}