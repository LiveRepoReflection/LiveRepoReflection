import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

public class Transaction {

    private final String txid;
    private final Map<String, String> serviceStatus;
    // Overall status can be "preparing", "committed", or "aborted".
    private String overallStatus;

    public Transaction(String txid) {
        this.txid = txid;
        this.serviceStatus = new HashMap<>();
        this.overallStatus = "preparing";
    }

    public String getTxid() {
        return txid;
    }

    public synchronized void addServiceStatus(String service, String status) {
        // Idempotency: do not override a failure status.
        if (serviceStatus.containsKey(service)) {
            String existingStatus = serviceStatus.get(service);
            if ("prepared".equals(existingStatus) && !"prepared".equals(status)) {
                serviceStatus.put(service, status);
            }
        } else {
            serviceStatus.put(service, status);
        }
    }

    public synchronized boolean allServicesPrepared() {
        for (String status : serviceStatus.values()) {
            if (!"prepared".equals(status)) {
                return false;
            }
        }
        return true;
    }

    public synchronized Set<String> getServices() {
        return Collections.unmodifiableSet(serviceStatus.keySet());
    }

    public synchronized String getStatus() {
        return overallStatus;
    }

    public synchronized void setOverallStatus(String status) {
        this.overallStatus = status;
    }
}