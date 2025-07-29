package tx_coordinator;

public class TransactionFailureException extends Exception {
    public TransactionFailureException(String message) {
        super(message);
    }
}