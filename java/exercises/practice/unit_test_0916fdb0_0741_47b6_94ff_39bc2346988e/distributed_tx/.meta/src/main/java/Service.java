package distributed_tx;

import java.util.UUID;

public interface Service {
    boolean prepare(UUID transactionId);
    void commit(UUID transactionId);
    void rollback(UUID transactionId);
}