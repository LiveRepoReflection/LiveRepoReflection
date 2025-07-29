/**
 * Represents the status of a distributed transaction.
 */
public enum TransactionStatus {
    /**
     * The transaction has been started but preparation has not begun.
     */
    ACTIVE,
    
    /**
     * The transaction is in the process of preparing (send prepare to all services).
     */
    PREPARING,
    
    /**
     * The transaction is in the process of committing (sending commit to all services).
     */
    COMMITTING,
    
    /**
     * The transaction is in the process of rolling back (sending rollback to all services).
     */
    ROLLING_BACK,
    
    /**
     * The transaction has been successfully committed.
     */
    COMMITTED,
    
    /**
     * The transaction has been rolled back.
     */
    ROLLED_BACK,
    
    /**
     * Result of the prepare phase - all services agreed to commit.
     */
    COMMIT,
    
    /**
     * Result of the prepare phase - at least one service voted to rollback.
     */
    ROLLBACK,
    
    /**
     * The status of the transaction is unknown, typically due to errors or timeouts.
     */
    UNKNOWN
}