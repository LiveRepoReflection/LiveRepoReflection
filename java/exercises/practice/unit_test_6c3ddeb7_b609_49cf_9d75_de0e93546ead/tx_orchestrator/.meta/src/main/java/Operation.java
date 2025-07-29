public class Operation {
    private final String serviceId;
    private final String operationData;
    private final String compensationData;

    public Operation(String serviceId, String operationData, String compensationData) {
        this.serviceId = serviceId;
        this.operationData = operationData;
        this.compensationData = compensationData;
    }

    public String getServiceId() {
        return serviceId;
    }

    public String getOperationData() {
        return operationData;
    }

    public String getCompensationData() {
        return compensationData;
    }
}