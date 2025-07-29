public interface ServiceParticipant {
    /**
     * Prepare the service for the given transaction.
     * This method should be idempotent.
     *
     * @param transactionId the unique identifier of the transaction
     * @return true if the service successfully prepared and is ready to commit; false otherwise.
     */
    boolean prepare(String transactionId);

    /**
     * Commit the changes for the given transaction.
     * This method should be idempotent.
     *
     * @param transactionId the unique identifier of the transaction
     */
    void commit(String transactionId);

    /**
     * Rollback the changes for the given transaction.
     * This method should be idempotent.
     *
     * @param transactionId the unique identifier of the transaction
     */
    void rollback(String transactionId);
}