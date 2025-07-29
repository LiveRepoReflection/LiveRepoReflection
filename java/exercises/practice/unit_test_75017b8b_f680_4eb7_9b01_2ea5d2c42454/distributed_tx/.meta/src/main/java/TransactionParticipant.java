public interface TransactionParticipant {
    /**
     * Prepare the participant for commit.
     * @return true if preparation is successful, false otherwise.
     */
    boolean prepare();

    /**
     * Commit the transaction.
     */
    void commit();

    /**
     * Rollback the transaction.
     */
    void rollback();
}