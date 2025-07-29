import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TransactionOutcome {
    private final String status;
    private final Map<String, String> resourceStates;
    private final List<String> conflictNotifications;

    public TransactionOutcome(String status, Map<String, String> resourceStates, List<String> conflictNotifications) {
        this.status = status;
        this.resourceStates = resourceStates;
        this.conflictNotifications = conflictNotifications;
    }

    public String getStatus() {
        return status;
    }

    public Map<String, String> getResourceStates() {
        return resourceStates;
    }

    public List<String> getConflictNotifications() {
        return conflictNotifications;
    }
}