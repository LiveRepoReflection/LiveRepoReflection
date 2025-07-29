package distributed_tx;

public class TransactionResult {
    private final String transactionId;
    private final TransactionState state;

    public TransactionResult(String transactionId, TransactionState state) {
        this.transactionId = transactionId;
        this.state = state;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public TransactionState getState() {
        return state;
    }
}