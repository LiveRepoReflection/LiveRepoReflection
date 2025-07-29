public interface Service {
    /**
     * Attempts to prepare the service for the transaction.
     * This operation must be idempotent.
     *
     * @param transactionId the unique transaction identifier.
     * @return true if the service has successfully prepared for the transaction; false otherwise.
     * @throws InterruptedException if the thread is interrupted during execution.
     */
    boolean prepare(String transactionId) throws InterruptedException;

    /**
     * Commits the transaction. This operation must be idempotent.
     *
     * @param transactionId the unique transaction identifier.
     */
    void commit(String transactionId);

    /**
     * Rolls back the transaction. This operation must be idempotent.
     *
     * @param transactionId the unique transaction identifier.
     */
    void rollback(String transactionId);
}