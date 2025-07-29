/**
 * Interface representing a participant in a distributed transaction.
 * A participant could be a database, a message queue, or any other service
 * that needs to participate in a distributed transaction.
 */
public interface Participant {

    /**
     * Prepares the participant for committing the transaction.
     * The participant should perform necessary checks and reserve resources.
     *
     * @param transactionId The unique identifier for the transaction
     * @return true if the participant is prepared to commit, false otherwise
     */
    boolean prepare(String transactionId);

    /**
     * Commits the transaction. This method is called only if the participant
     * returned true from the prepare method.
     *
     * @param transactionId The unique identifier for the transaction
     * @return true if the commit was successful, false otherwise
     */
    boolean commit(String transactionId);

    /**
     * Rolls back the transaction. This method is called if any participant
     * fails to prepare or if an explicit rollback is requested.
     *
     * @param transactionId The unique identifier for the transaction
     * @return true if the rollback was successful, false otherwise
     */
    boolean rollback(String transactionId);
}