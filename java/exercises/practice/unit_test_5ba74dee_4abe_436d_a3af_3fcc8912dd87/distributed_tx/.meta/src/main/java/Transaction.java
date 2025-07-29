import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public class Transaction {
    private final String id;
    private final Map<String, String> operations;

    public Transaction(String id) {
        if (id == null) {
            throw new IllegalArgumentException("Transaction ID cannot be null");
        }
        if (id.trim().isEmpty()) {
            throw new IllegalArgumentException("Transaction ID cannot be empty");
        }
        this.id = id;
        this.operations = new HashMap<>();
    }

    public void addOperation(String serviceId, String operation) {
        if (serviceId == null) {
            throw new IllegalArgumentException("Service ID cannot be null");
        }
        if (operation == null) {
            throw new IllegalArgumentException("Operation cannot be null");
        }
        operations.put(serviceId, operation);
    }

    public String getId() {
        return id;
    }

    public Map<String, String> getOperations() {
        return Collections.unmodifiableMap(operations);
    }
}