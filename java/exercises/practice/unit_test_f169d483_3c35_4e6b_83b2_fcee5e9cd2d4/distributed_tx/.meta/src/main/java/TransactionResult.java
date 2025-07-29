import java.io.Serializable;

public class TransactionResult implements Serializable {
    private final boolean successful;
    private final String message;

    public TransactionResult(boolean successful, String message) {
        this.successful = successful;
        this.message = message;
    }

    public boolean isSuccessful() {
        return successful;
    }

    public String getMessage() {
        return message;
    }
}