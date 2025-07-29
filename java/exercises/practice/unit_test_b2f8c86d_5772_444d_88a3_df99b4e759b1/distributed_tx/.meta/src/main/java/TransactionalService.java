public interface TransactionalService {
    /**
     * Prepare the service for commit. This method should perform all necessary checks
     * and return true if the service is ready to commit, or false otherwise.
     */
    boolean prepare();

    /**
     * Commit the transaction. This method should be idempotent.
     */
    void commit();

    /**
     * Rollback the transaction. This method should be idempotent.
     */
    void rollback();
}