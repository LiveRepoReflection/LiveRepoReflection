package distributed_tx;

import java.util.Map;
import java.util.UUID;

public class TransactionCoordinator {
    private long timeoutMillis;

    /**
     * Constructs a TransactionCoordinator with a default timeout of 500 milliseconds.
     */
    public TransactionCoordinator() {
        this.timeoutMillis = 500;
    }

    /**
     * Constructs a TransactionCoordinator with a specified timeout.
     * @param timeoutMillis timeout in milliseconds for branch responses.
     */
    public TransactionCoordinator(long timeoutMillis) {
        this.timeoutMillis = timeoutMillis;
    }

    /**
     * Processes a distributed transaction using the two-phase commit protocol.
     *
     * Phase 1: Sends prepare requests to all branches.
     * Phase 2: If all branches prepare successfully, commits; otherwise rolls back.
     *
     * @param transactionId A unique transaction identifier.
     * @param operations A map where the key is a Branch instance and the value is the operation details.
     * @return true if the transaction commits, false if it rolls back.
     */
    public boolean processTransaction(UUID transactionId, Map<Branch, String> operations) {
        long startTime = System.currentTimeMillis();
        // Phase 1: Prepare
        for (Map.Entry<Branch, String> entry : operations.entrySet()) {
            Branch branch = entry.getKey();
            boolean prepared = false;
            try {
                prepared = branch.prepare(transactionId, entry.getValue());
                // Check if the overall transaction is taking too long
                if (System.currentTimeMillis() - startTime > timeoutMillis) {
                    prepared = false;
                }
            } catch (Exception e) {
                prepared = false;
            }
            if (!prepared) {
                rollbackAll(transactionId, operations);
                return false;
            }
        }
        // Phase 2: Commit
        for (Branch branch : operations.keySet()) {
            branch.commit(transactionId);
        }
        return true;
    }

    /**
     * Sends a rollback request to every branch participating in the transaction.
     * @param transactionId A unique transaction identifier.
     * @param operations A map of branches participating in the transaction.
     */
    private void rollbackAll(UUID transactionId, Map<Branch, String> operations) {
        for (Branch branch : operations.keySet()) {
            try {
                branch.rollback(transactionId);
            } catch (Exception e) {
                // Exceptions during rollback are ignored to ensure all branches are attempted.
            }
        }
    }
}