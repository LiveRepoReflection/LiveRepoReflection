package distributed_tx;

import java.util.UUID;

public class TransactionContext {
    private final UUID transactionId;

    public TransactionContext(UUID transactionId) {
        this.transactionId = transactionId;
    }

    public UUID getTransactionId() {
        return transactionId;
    }
}