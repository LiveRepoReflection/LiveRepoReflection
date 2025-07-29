/**
 * Represents the response of a participant during the prepare phase.
 */
public enum ParticipantStatus {
    /**
     * Participant has successfully prepared and is ready to commit.
     */
    PREPARED,
    
    /**
     * Participant cannot prepare and wants to abort the transaction.
     */
    ABORT
}