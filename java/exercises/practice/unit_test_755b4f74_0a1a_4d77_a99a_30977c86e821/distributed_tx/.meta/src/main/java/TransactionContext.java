package distributed_tx;

import java.util.UUID;

public class TransactionContext {
    private final UUID transactionId = UUID.randomUUID();

    public UUID getTransactionId() {
        return transactionId;
    }
}