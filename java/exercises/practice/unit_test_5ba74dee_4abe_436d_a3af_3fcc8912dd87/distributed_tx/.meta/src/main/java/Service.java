public interface Service {
    boolean prepare(String txId, String operation);
    void commit(String txId);
    void rollback(String txId);
}