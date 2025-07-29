package distributed_tx;

import java.util.ArrayList;
import java.util.List;

public class Transaction {
    private final String id;
    private final List<String> operations;

    public Transaction(String id) {
        this.id = id;
        this.operations = new ArrayList<>();
    }

    public String getId() {
        return id;
    }

    public List<String> getOperations() {
        return operations;
    }

    public void addOperation(String operation) {
        operations.add(operation);
    }
}