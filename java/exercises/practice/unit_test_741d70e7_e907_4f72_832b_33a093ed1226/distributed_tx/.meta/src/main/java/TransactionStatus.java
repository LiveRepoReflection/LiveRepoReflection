/**
 * Represents the status of a distributed transaction.
 */
public enum TransactionStatus {
    /**
     * Transaction has been initiated but not yet prepared or committed.
     */
    ACTIVE,
    
    /**
     * Transaction is in the process of preparing all participants.
     */
    PREPARING,
    
    /**
     * All participants have successfully prepared.
     */
    PREPARED,
    
    /**
     * Transaction is in the process of committing all participants.
     */
    COMMITTING,
    
    /**
     * Transaction has been successfully committed.
     */
    COMMITTED,
    
    /**
     * Transaction has been rolled back.
     */
    ROLLED_BACK
}