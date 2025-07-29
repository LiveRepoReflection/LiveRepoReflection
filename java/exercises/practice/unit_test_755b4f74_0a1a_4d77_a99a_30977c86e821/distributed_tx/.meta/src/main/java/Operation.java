package distributed_tx;

public class Operation {
    private final String serviceName;
    private final String operationDetails;

    public Operation(String serviceName, String operationDetails) {
        this.serviceName = serviceName;
        this.operationDetails = operationDetails;
    }

    public String getServiceName() {
        return serviceName;
    }

    public String getOperationDetails() {
        return operationDetails;
    }
}