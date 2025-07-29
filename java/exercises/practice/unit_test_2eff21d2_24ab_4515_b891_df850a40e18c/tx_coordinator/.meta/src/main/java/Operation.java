package tx_coordinator;

public class Operation {
    private final String storageNodeId;
    private final String operationType;
    private final String dataKey;
    private final String dataValue;

    public Operation(String storageNodeId, String operationType, String dataKey, String dataValue) {
        this.storageNodeId = storageNodeId;
        this.operationType = operationType;
        this.dataKey = dataKey;
        this.dataValue = dataValue;
    }

    public String getStorageNodeId() {
        return storageNodeId;
    }

    public String getOperationType() {
        return operationType;
    }

    public String getDataKey() {
        return dataKey;
    }

    public String getDataValue() {
        return dataValue;
    }
}