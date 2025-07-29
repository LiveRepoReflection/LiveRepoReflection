package distributed_tx;

import java.util.List;
import java.util.UUID;

public class LogEntry {
    private final UUID transactionId;
    private final String decision;
    private final List<String> serviceIds;

    public LogEntry(UUID transactionId, String decision, List<String> serviceIds) {
        this.transactionId = transactionId;
        this.decision = decision;
        this.serviceIds = serviceIds;
    }

    public UUID getTransactionId() {
        return transactionId;
    }

    public String getDecision() {
        return decision;
    }

    public List<String> getServiceIds() {
        return serviceIds;
    }

    @Override
    public String toString() {
        return "LogEntry{" +
                "transactionId=" + transactionId +
                ", decision='" + decision + '\'' +
                ", serviceIds=" + serviceIds +
                '}';
    }
}