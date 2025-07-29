import java.util.HashMap;
import java.util.Map;

public class Worker {
    private final String workerId;
    private final Map<String, Integer> availableResources;
    private final int heartbeatInterval; // in seconds
    private long lastHeartbeatTime;
    
    public Worker(String workerId, Map<String, Integer> availableResources, int heartbeatInterval) {
        this.workerId = workerId;
        // Make a deep copy of available resources.
        this.availableResources = new HashMap<>();
        for (Map.Entry<String, Integer> entry : availableResources.entrySet()) {
            this.availableResources.put(entry.getKey(), entry.getValue());
        }
        this.heartbeatInterval = heartbeatInterval;
        updateHeartbeat();
    }
    
    public String getWorkerId() {
        return workerId;
    }
    
    public Map<String, Integer> getAvailableResources() {
        return availableResources;
    }
    
    public int getHeartbeatInterval() {
        return heartbeatInterval;
    }
    
    public long getLastHeartbeatTime() {
        return lastHeartbeatTime;
    }
    
    public void updateHeartbeat() {
        lastHeartbeatTime = System.currentTimeMillis();
    }
    
    // Check if the worker is alive based on heartbeat interval.
    public boolean isAlive() {
        long currentTime = System.currentTimeMillis();
        // Allow a buffer of 2 heartbeat intervals
        return (currentTime - lastHeartbeatTime) <= (heartbeatInterval * 2000L);
    }
}