package distributed_tx;

import java.util.UUID;

public interface ResourceManager {
    /**
     * Prepare the resource for commit.
     * @param transactionId the transaction identifier.
     * @return true if preparation is successful, false otherwise.
     */
    boolean prepare(UUID transactionId);

    /**
     * Commit the resource's changes.
     * @param transactionId the transaction identifier.
     */
    void commit(UUID transactionId);

    /**
     * Rollback any changes made for this transaction.
     * @param transactionId the transaction identifier.
     */
    void rollback(UUID transactionId);
}