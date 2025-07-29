package distributed_tx;

import java.util.UUID;

public interface Microservice {
    String prepare(UUID transactionId);
    void commit(UUID transactionId);
    void rollback(UUID transactionId);
}