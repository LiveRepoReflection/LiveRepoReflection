/**
 * Interface that must be implemented by all services participating
 * in a distributed transaction.
 */
public interface ParticipantService {
    
    /**
     * Prepare the participant for a transaction. This is the first phase
     * of the two-phase commit protocol.
     * 
     * @param transactionId the transaction ID
     * @return status indicating if the participant is ready to commit
     */
    ParticipantStatus prepare(String transactionId);
    
    /**
     * Commit the transaction. This is the second phase of the two-phase
     * commit protocol and is called only if all participants voted to commit.
     * 
     * @param transactionId the transaction ID
     */
    void commit(String transactionId);
    
    /**
     * Rollback the transaction. This is called if any participant voted to abort
     * during the prepare phase, or if an error occurred.
     * 
     * @param transactionId the transaction ID
     */
    void rollback(String transactionId);
    
    /**
     * Get the name of the participant service for logging purposes.
     * 
     * @return the name of the service
     */
    String getName();
}