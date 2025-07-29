package distributed_tx;

public interface Participant {
    /**
     * Attempt to prepare the transaction.
     * @return true if this participant votes to commit, false to vote to abort.
     */
    boolean prepare();
    
    /**
     * Permanently commit the transaction.
     */
    void commit();
    
    /**
     * Rollback any tentative changes.
     */
    void rollback();
}