/**
 * Interface for a participant in a distributed transaction.
 * Participants must implement the two-phase commit protocol.
 */
public interface Participant {
    /**
     * Prepares the participant for the transaction.
     * This is the first phase of the two-phase commit protocol.
     *
     * @return true if the participant is prepared to commit, false otherwise
     */
    boolean prepare();
    
    /**
     * Commits the transaction.
     * This is called in the second phase if all participants prepared successfully.
     */
    void commit();
    
    /**
     * Rolls back the transaction.
     * This is called in the second phase if any participant failed to prepare.
     */
    void rollback();
}