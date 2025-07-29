package distributed_tx;

public class Order {
    private String orderId;
    private Status status;
    private boolean simulatePaymentFailure;
    private boolean compensationExecuted;
    private int processingCount;
    private String inventoryItemId;

    public enum Status {
        NEW, PROCESSING, COMPLETED, FAILED
    }

    public Order(String orderId, Status status) {
        this.orderId = orderId;
        this.status = status;
        this.simulatePaymentFailure = false;
        this.compensationExecuted = false;
        this.processingCount = 0;
        this.inventoryItemId = null;
    }
    
    public String getOrderId() {
        return orderId;
    }

    public Status getStatus() {
        return status;
    }
    
    public void setStatus(Status status) {
        this.status = status;
    }
    
    public boolean isSimulatePaymentFailure() {
        return simulatePaymentFailure;
    }
    
    public void setSimulatePaymentFailure(boolean simulatePaymentFailure) {
        this.simulatePaymentFailure = simulatePaymentFailure;
    }
    
    public boolean isCompensationExecuted() {
        return compensationExecuted;
    }
    
    public void setCompensationExecuted(boolean compensationExecuted) {
        this.compensationExecuted = compensationExecuted;
    }
    
    public int getProcessingCount() {
        return processingCount;
    }
    
    public void incrementProcessingCount() {
        this.processingCount++;
    }
    
    public String getInventoryItemId() {
        return inventoryItemId;
    }
    
    public void setInventoryItemId(String inventoryItemId) {
        this.inventoryItemId = inventoryItemId;
    }
}