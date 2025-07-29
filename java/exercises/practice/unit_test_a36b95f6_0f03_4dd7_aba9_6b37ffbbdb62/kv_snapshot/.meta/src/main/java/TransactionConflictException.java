package kv_snapshot;

public class TransactionConflictException extends Exception {
    public TransactionConflictException(String message) {
        super(message);
    }
}