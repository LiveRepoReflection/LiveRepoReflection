import java.util.List;

public class TransactionResult {
    private final boolean success;
    private final List<TransactionStatus> transactionStatuses;

    public TransactionResult(boolean success, List<TransactionStatus> transactionStatuses) {
        this.success = success;
        this.transactionStatuses = transactionStatuses;
    }

    public boolean isSuccess() {
        return success;
    }

    public List<TransactionStatus> getTransactionStatuses() {
        return transactionStatuses;
    }
}