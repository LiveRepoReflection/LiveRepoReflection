public interface Shard {
    /**
     * Attempt to prepare the local transaction.
     * Return true if successful, false otherwise.
     */
    boolean prepare(String transactionId);
    
    /**
     * Commit the local transaction.
     */
    void commit(String transactionId);
    
    /**
     * Rollback the local transaction.
     */
    void rollback(String transactionId);
}