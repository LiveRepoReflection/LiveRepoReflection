import java.util.UUID;

public interface TransactionalService {
    boolean prepare(UUID transactionId, Object data);
    boolean commit(UUID transactionId);
    boolean rollback(UUID transactionId);
}