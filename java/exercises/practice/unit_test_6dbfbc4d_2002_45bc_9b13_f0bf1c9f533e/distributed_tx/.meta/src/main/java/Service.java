public interface Service {
    boolean prepare(String transactionId);
    void commit(String transactionId);
    void rollback(String transactionId);
    String getServiceName();
}