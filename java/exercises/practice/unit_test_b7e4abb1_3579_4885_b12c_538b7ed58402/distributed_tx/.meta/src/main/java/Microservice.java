public interface Microservice {
    // Prepare phase: return true if the service is ready for commit, false otherwise.
    boolean prepare(String transactionId);
    
    // Commit the transaction, may throw an exception on failure.
    void commit(String transactionId) throws Exception;
    
    // Rollback the transaction, may throw an exception on failure.
    void rollback(String transactionId) throws Exception;
}