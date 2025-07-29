package distributed_tx;

public class TransactionResult {
    public enum Status {
        SUCCESS, FAILED
    }
    
    private Status status;
    
    public TransactionResult(Status status) {
        this.status = status;
    }
    
    public Status getStatus() {
        return status;
    }
    
    public void setStatus(Status status) {
        this.status = status;
    }
}