import java.util.List;

public class Transaction {
    private String id;
    private List<String> serviceIds;
    private String operation;

    public Transaction(String id, List<String> serviceIds, String operation) {
        this.id = id;
        this.serviceIds = serviceIds;
        this.operation = operation;
    }

    public String getId() {
        return id;
    }

    public List<String> getServiceIds() {
        return serviceIds;
    }

    public String getOperation() {
        return operation;
    }
}