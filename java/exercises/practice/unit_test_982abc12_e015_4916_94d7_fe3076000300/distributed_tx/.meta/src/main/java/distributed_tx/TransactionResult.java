package distributed_tx;

public class TransactionResult {
    private final boolean committed;

    public TransactionResult(boolean committed) {
        this.committed = committed;
    }

    public boolean isCommitted() {
        return committed;
    }
}