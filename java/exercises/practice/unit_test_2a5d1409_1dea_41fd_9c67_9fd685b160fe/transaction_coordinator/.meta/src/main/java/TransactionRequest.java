package transaction_coordinator;

import java.util.Map;

public class TransactionRequest {
    private final Map<String, String> operations;

    /**
     * Constructs a TransactionRequest.
     * @param operations A map from participant IDs to their corresponding operations.
     */
    public TransactionRequest(Map<String, String> operations) {
        this.operations = operations;
    }

    /**
     * Returns the operations associated with this transaction.
     * @return Map of participant IDs to operation descriptions.
     */
    public Map<String, String> getOperations() {
        return operations;
    }
}