import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class DefaultService implements Service {
    private final String id;
    private final Map<String, String> preparedOperations;
    private final Map<String, String> committedOperations;

    public DefaultService(String id) {
        this.id = id;
        this.preparedOperations = new ConcurrentHashMap<>();
        this.committedOperations = new ConcurrentHashMap<>();
    }

    @Override
    public boolean prepare(String txId, String operation) {
        try {
            // Simulate some work
            Thread.sleep(100);
            preparedOperations.put(txId, operation);
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    @Override
    public void commit(String txId) {
        String operation = preparedOperations.remove(txId);
        if (operation != null) {
            committedOperations.put(txId, operation);
        }
    }

    @Override
    public void rollback(String txId) {
        preparedOperations.remove(txId);
    }

    public Map<String, String> getCommittedOperations() {
        return committedOperations;
    }
}