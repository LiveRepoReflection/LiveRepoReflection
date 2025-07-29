/**
 * Represents a service that participates in a distributed transaction.
 */
public interface ServiceEndpoint {
    
    /**
     * Called during the prepare phase of two-phase commit.
     * The service should indicate whether it's ready to commit or needs to roll back.
     * 
     * @return The service's response (COMMIT, ROLLBACK, or ERROR)
     */
    ServiceResponse prepare();
    
    /**
     * Called to commit the transaction.
     * This method should be idempotent - calling it multiple times should have
     * the same effect as calling it once.
     */
    void commit();
    
    /**
     * Called to roll back the transaction.
     * This method should be idempotent - calling it multiple times should have
     * the same effect as calling it once.
     */
    void rollback();
}