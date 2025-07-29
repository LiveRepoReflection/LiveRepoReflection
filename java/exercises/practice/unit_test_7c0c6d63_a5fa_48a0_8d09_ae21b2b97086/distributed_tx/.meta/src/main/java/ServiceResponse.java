/**
 * Represents possible responses from a service during the prepare phase.
 */
public enum ServiceResponse {
    /**
     * The service is ready to commit the transaction.
     */
    COMMIT,
    
    /**
     * The service needs to roll back the transaction.
     */
    ROLLBACK,
    
    /**
     * The service encountered an error and cannot proceed with the transaction.
     */
    ERROR
}