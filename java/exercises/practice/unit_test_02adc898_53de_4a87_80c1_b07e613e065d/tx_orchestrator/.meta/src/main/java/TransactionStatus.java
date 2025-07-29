public class TransactionStatus {
    public enum Status {
        COMMITTED,
        ROLLED_BACK,
        COMMIT_FAILED,
        ROLLBACK_FAILED
    }

    private final Status status;
    private final String errorMessage;

    public TransactionStatus(Status status, String errorMessage) {
        this.status = status;
        this.errorMessage = errorMessage;
    }

    public Status getStatus() {
        return status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}