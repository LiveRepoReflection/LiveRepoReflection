import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Optional server monitoring system to track load on each server.
 * This can be used with the load balancer to implement dynamic weight adjustment.
 */
public class ServerMonitor {
    // Map of server ID to its current load (request count)
    private final Map<String, AtomicInteger> serverLoads = new ConcurrentHashMap<>();
    
    // Map of server ID to its maximum capacity (for calculating utilization)
    private final Map<String, Integer> serverCapacities = new HashMap<>();
    
    // Track when servers were last seen alive
    private final Map<String, Long> serverLastSeen = new ConcurrentHashMap<>();
    
    // Lock for managing server capacities
    private final ReadWriteLock capacityLock = new ReentrantReadWriteLock();
    
    // Time after which a server is considered unresponsive (in milliseconds)
    private final long serverTimeoutMs;
    
    /**
     * Creates a new instance of the ServerMonitor with a default timeout of 30 seconds.
     */
    public ServerMonitor() {
        this(30000); // 30 seconds default timeout
    }
    
    /**
     * Creates a new instance of the ServerMonitor.
     * 
     * @param serverTimeoutMs Time in milliseconds after which a server is considered down
     */
    public ServerMonitor(long serverTimeoutMs) {
        this.serverTimeoutMs = serverTimeoutMs;
    }
    
    /**
     * Registers a server with the monitor.
     * 
     * @param serverId The ID of the server
     * @param capacity The maximum capacity of the server (used for utilization calculations)
     */
    public void registerServer(String serverId, int capacity) {
        serverLoads.putIfAbsent(serverId, new AtomicInteger(0));
        serverLastSeen.put(serverId, System.currentTimeMillis());
        
        capacityLock.writeLock().lock();
        try {
            serverCapacities.put(serverId, capacity);
        } finally {
            capacityLock.writeLock().unlock();
        }
    }
    
    /**
     * Unregisters a server from the monitor.
     * 
     * @param serverId The ID of the server
     */
    public void unregisterServer(String serverId) {
        serverLoads.remove(serverId);
        serverLastSeen.remove(serverId);
        
        capacityLock.writeLock().lock();
        try {
            serverCapacities.remove(serverId);
        } finally {
            capacityLock.writeLock().unlock();
        }
    }
    
    /**
     * Records that a request was sent to a server.
     * 
     * @param serverId The ID of the server
     */
    public void recordRequest(String serverId) {
        AtomicInteger load = serverLoads.get(serverId);
        if (load != null) {
            load.incrementAndGet();
        }
    }
    
    /**
     * Records that a request was completed by a server.
     * 
     * @param serverId The ID of the server
     */
    public void recordResponse(String serverId) {
        AtomicInteger load = serverLoads.get(serverId);
        if (load != null) {
            load.decrementAndGet();
        }
        serverLastSeen.put(serverId, System.currentTimeMillis());
    }
    
    /**
     * Gets the current load (number of active requests) for a server.
     * 
     * @param serverId The ID of the server
     * @return The current load, or 0 if the server is not registered
     */
    public int getServerLoad(String serverId) {
        AtomicInteger load = serverLoads.get(serverId);
        return load != null ? load.get() : 0;
    }
    
    /**
     * Gets the current utilization percentage for a server.
     * 
     * @param serverId The ID of the server
     * @return The utilization percentage (0-100), or 0 if the server is not registered or has zero capacity
     */
    public double getServerUtilization(String serverId) {
        AtomicInteger load = serverLoads.get(serverId);
        if (load == null) {
            return 0.0;
        }
        
        capacityLock.readLock().lock();
        try {
            Integer capacity = serverCapacities.get(serverId);
            if (capacity == null || capacity == 0) {
                return 0.0;
            }
            
            return (load.get() * 100.0) / capacity;
        } finally {
            capacityLock.readLock().unlock();
        }
    }
    
    /**
     * Checks if a server is responsive.
     * 
     * @param serverId The ID of the server
     * @return true if the server is responsive, false otherwise
     */
    public boolean isServerAlive(String serverId) {
        Long lastSeen = serverLastSeen.get(serverId);
        if (lastSeen == null) {
            return false;
        }
        
        return (System.currentTimeMillis() - lastSeen) <= serverTimeoutMs;
    }
    
    /**
     * Gets a map of all server IDs to their current loads.
     * 
     * @return Map from server ID to current load
     */
    public Map<String, Integer> getAllServerLoads() {
        Map<String, Integer> loads = new HashMap<>();
        for (Map.Entry<String, AtomicInteger> entry : serverLoads.entrySet()) {
            loads.put(entry.getKey(), entry.getValue().get());
        }
        return loads;
    }
    
    /**
     * Gets a map of all server IDs to their current utilization percentages.
     * 
     * @return Map from server ID to utilization percentage
     */
    public Map<String, Double> getAllServerUtilizations() {
        Map<String, Double> utilizations = new HashMap<>();
        
        capacityLock.readLock().lock();
        try {
            for (String serverId : serverCapacities.keySet()) {
                utilizations.put(serverId, getServerUtilization(serverId));
            }
        } finally {
            capacityLock.readLock().unlock();
        }
        
        return utilizations;
    }
}