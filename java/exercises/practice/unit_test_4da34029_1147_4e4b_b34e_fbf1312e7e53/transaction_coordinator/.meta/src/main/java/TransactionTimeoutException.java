package transaction_coordinator;

public class TransactionTimeoutException extends Exception {
    public TransactionTimeoutException(String message) {
        super(message);
    }
}