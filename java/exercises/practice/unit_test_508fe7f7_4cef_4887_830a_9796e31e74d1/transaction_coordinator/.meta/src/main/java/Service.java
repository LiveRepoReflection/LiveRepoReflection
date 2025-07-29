import java.util.UUID;

public interface Service {
    boolean prepare(UUID transactionId, OperationData operationData);
    void commit(UUID transactionId);
    void rollback(UUID transactionId);
}