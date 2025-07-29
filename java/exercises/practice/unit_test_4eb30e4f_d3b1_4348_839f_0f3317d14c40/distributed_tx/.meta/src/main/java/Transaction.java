import java.util.ArrayList;
import java.util.List;

public class Transaction {
    private final String id;
    private final List<MicroserviceOperation> operations = new ArrayList<>();

    public Transaction(String id) {
        this.id = id;
    }

    public String getId() {
        return id;
    }

    public void addOperation(MicroserviceOperation op) {
        operations.add(op);
    }

    public List<MicroserviceOperation> getOperations() {
        return operations;
    }
}