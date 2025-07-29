public class Operation {
    private final String resourceId;
    private final OperationType type;
    private final String data;

    public Operation(String resourceId, OperationType type, String data) {
        this.resourceId = resourceId;
        this.type = type;
        this.data = data;
    }

    public String getResourceId() {
        return resourceId;
    }

    public OperationType getType() {
        return type;
    }

    public String getData() {
        return data;
    }
}