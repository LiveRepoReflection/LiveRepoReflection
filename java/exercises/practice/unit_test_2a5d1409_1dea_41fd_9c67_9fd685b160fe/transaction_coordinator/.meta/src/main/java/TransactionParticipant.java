package transaction_coordinator;

public interface TransactionParticipant {
    /**
     * Prepares the participant for committing the operation associated with the given transaction.
     * @param txId Unique transaction identifier.
     * @param operation Description of the operation to be performed.
     * @return true if the participant is ready to commit (vote-commit), false otherwise (vote-abort).
     */
    boolean prepare(String txId, String operation);

    /**
     * Commits the operation associated with the given transaction. This method must be idempotent.
     * @param txId Unique transaction identifier.
     */
    void commit(String txId);

    /**
     * Rolls back any changes associated with the given transaction. This method must be idempotent.
     * @param txId Unique transaction identifier.
     */
    void rollback(String txId);
}