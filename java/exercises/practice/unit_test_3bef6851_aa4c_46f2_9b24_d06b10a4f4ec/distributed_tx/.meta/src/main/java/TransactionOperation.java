package distributed_tx;

public class TransactionOperation {
    private int serviceId;
    private OperationType operationType;
    private int amount;

    public TransactionOperation(int serviceId, OperationType operationType, int amount) {
        this.serviceId = serviceId;
        this.operationType = operationType;
        this.amount = amount;
    }

    public int getServiceId() {
        return serviceId;
    }

    public OperationType getOperationType() {
        return operationType;
    }

    public int getAmount() {
        return amount;
    }
}