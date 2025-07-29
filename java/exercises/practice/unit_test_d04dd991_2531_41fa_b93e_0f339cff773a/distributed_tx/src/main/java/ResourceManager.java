import java.util.UUID;

public interface ResourceManager {
    boolean prepare(UUID tid, String operationDetails);
    void commit(UUID tid);
    void rollback(UUID tid);
}