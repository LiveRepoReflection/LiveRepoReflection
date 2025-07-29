import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Transaction {
    private final UUID id;
    private TransactionStatus status;
    private final List<String> operations;

    public Transaction() {
        this.id = UUID.randomUUID();
        this.status = TransactionStatus.INIT;
        this.operations = new ArrayList<>();
    }

    public UUID getId() {
        return id;
    }

    public TransactionStatus getStatus() {
        return status;
    }

    public void setStatus(TransactionStatus status) {
        this.status = status;
    }

    public List<String> getOperations() {
        return operations;
    }

    public void addOperation(String op) {
        operations.add(op);
    }
}