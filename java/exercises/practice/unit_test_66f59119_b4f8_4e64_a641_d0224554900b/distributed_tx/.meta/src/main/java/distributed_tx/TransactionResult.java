package distributed_tx;

public class TransactionResult {
    private Transaction transaction;
    private TransactionStatus status;

    public TransactionResult(Transaction transaction, TransactionStatus status) {
        this.transaction = transaction;
        this.status = status;
    }

    public Transaction getTransaction() {
        return transaction;
    }

    public TransactionStatus getStatus() {
        return status;
    }

    public void setStatus(TransactionStatus status) {
        this.status = status;
    }
}