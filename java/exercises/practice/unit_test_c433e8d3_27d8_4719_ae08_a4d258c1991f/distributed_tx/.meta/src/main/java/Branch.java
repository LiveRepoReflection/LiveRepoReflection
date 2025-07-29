package distributed_tx;

import java.util.UUID;

public interface Branch {
    /**
     * Attempts to tentatively perform the operation for a given transaction.
     * @param transactionId Unique identifier for the transaction.
     * @param operationDetails Details of the operation (e.g., debit/credit information).
     * @return true if the branch is prepared to commit; false if preparation fails.
     */
    boolean prepare(UUID transactionId, String operationDetails);

    /**
     * Permanently commits the tentative operation for the transaction.
     * @param transactionId Unique identifier for the transaction.
     */
    void commit(UUID transactionId);

    /**
     * Rolls back the tentative operation made during the prepare phase.
     * @param transactionId Unique identifier for the transaction.
     */
    void rollback(UUID transactionId);
}