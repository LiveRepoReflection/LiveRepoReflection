package distributed_tx;

import java.util.List;

public class Transaction {
    private final String transactionId;
    private final List<Operation> operations;

    public Transaction(String transactionId, List<Operation> operations) {
        this.transactionId = transactionId;
        this.operations = operations;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public List<Operation> getOperations() {
        return operations;
    }
}