package tx_coordinator;

import java.util.UUID;

public interface Service {
    boolean prepare(UUID transactionId) throws Exception;
    void commit(UUID transactionId) throws Exception;
    void rollback(UUID transactionId) throws Exception;
}