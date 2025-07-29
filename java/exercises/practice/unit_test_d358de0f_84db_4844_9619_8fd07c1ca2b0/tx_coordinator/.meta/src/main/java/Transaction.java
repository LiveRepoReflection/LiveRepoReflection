import java.util.ArrayList;
import java.util.List;

public class Transaction {
    private final String transactionId;
    private final List<Operation> operations;

    public Transaction(String transactionId) {
        this.transactionId = transactionId;
        this.operations = new ArrayList<>();
    }

    public String getTransactionId() {
        return transactionId;
    }

    public List<Operation> getOperations() {
        return operations;
    }

    public void addOperation(Operation op) {
        operations.add(op);
    }
}