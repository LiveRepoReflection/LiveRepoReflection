public class TransactionResult {
    private final boolean successful;
    private final String message;
    private final TransactionState finalState;

    public TransactionResult(boolean successful, String message, TransactionState finalState) {
        this.successful = successful;
        this.message = message;
        this.finalState = finalState;
    }

    public boolean isSuccessful() {
        return successful;
    }

    public String getMessage() {
        return message;
    }

    public TransactionState getFinalState() {
        return finalState;
    }
}