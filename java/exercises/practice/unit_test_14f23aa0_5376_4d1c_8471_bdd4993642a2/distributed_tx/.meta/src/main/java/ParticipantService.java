import java.util.Map;

public interface ParticipantService {
    boolean prepare(String transactionId, Map<String, Object> data);
    boolean commit(String transactionId);
    boolean rollback(String transactionId);
}