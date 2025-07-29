import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.stream.Collectors;

/**
 * A load balancer implementation using consistent hashing algorithm.
 * This implementation uses virtual nodes to ensure even distribution of load.
 */
public class ConsistentHashLoadBalancer {
    // Number of virtual nodes per weight unit
    private static final int VIRTUAL_NODES_PER_WEIGHT = 40;
    
    // Physical servers with their weights
    private final Map<String, Integer> servers = new HashMap<>();
    
    // The hash ring - maps hash positions to server IDs
    private final SortedMap<Integer, String> ring = new TreeMap<>();
    
    // Concurrency control
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    // MessageDigest instance for computing hash values
    private final MessageDigest md;
    
    /**
     * Creates a new instance of the ConsistentHashLoadBalancer.
     */
    public ConsistentHashLoadBalancer() {
        try {
            md = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not available", e);
        }
    }
    
    /**
     * Adds a server to the load balancer.
     * 
     * @param serverId The unique ID of the server
     * @param weight The weight of the server (must be positive)
     * @return true if the server was added, false if it already existed
     * @throws IllegalArgumentException if weight is less than or equal to zero
     */
    public boolean addServer(String serverId, int weight) {
        if (weight <= 0) {
            throw new IllegalArgumentException("Server weight must be positive");
        }
        
        lock.writeLock().lock();
        try {
            // Check if server already exists
            if (servers.containsKey(serverId)) {
                return false;
            }
            
            // Add the server to our list
            servers.put(serverId, weight);
            
            // Add virtual nodes to the hash ring
            addVirtualNodes(serverId, weight);
            
            return true;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Removes a server from the load balancer.
     * 
     * @param serverId The unique ID of the server to remove
     * @return true if the server was removed, false if it wasn't found
     */
    public boolean removeServer(String serverId) {
        lock.writeLock().lock();
        try {
            // Check if server exists
            if (!servers.containsKey(serverId)) {
                return false;
            }
            
            // Remove the server from our list
            int weight = servers.remove(serverId);
            
            // Remove all virtual nodes for this server
            removeVirtualNodes(serverId, weight);
            
            return true;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    /**
     * Gets the server responsible for the given key.
     * 
     * @param key The key to route
     * @return The server ID responsible for the key
     * @throws IllegalArgumentException if key is null
     * @throws IllegalStateException if no servers are available
     */
    public String getServer(String key) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }
        
        lock.readLock().lock();
        try {
            if (ring.isEmpty()) {
                throw new IllegalStateException("No servers available");
            }
            
            // Calculate the hash of the key
            int hash = getHash(key);
            
            // Find the first server on the ring at or after the hash position
            SortedMap<Integer, String> tailMap = ring.tailMap(hash);
            int ringPosition = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();
            
            // Return the server at that position
            return ring.get(ringPosition);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Gets all currently registered server IDs.
     * 
     * @return Collection of server IDs
     */
    public Collection<String> getServers() {
        lock.readLock().lock();
        try {
            return servers.keySet().stream().collect(Collectors.toList());
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Gets the distribution statistics showing how many virtual nodes each server has.
     * 
     * @return Map from server ID to count of virtual nodes
     */
    public Map<String, Integer> getDistributionStatistics() {
        lock.readLock().lock();
        try {
            Map<String, Integer> stats = new HashMap<>();
            for (String serverId : servers.keySet()) {
                stats.put(serverId, 0);
            }
            
            for (String serverId : ring.values()) {
                stats.put(serverId, stats.get(serverId) + 1);
            }
            
            return stats;
        } finally {
            lock.readLock().unlock();
        }
    }
    
    // Adds virtual nodes for a server to the hash ring
    private void addVirtualNodes(String serverId, int weight) {
        int numVirtualNodes = weight * VIRTUAL_NODES_PER_WEIGHT;
        
        for (int i = 0; i < numVirtualNodes; i++) {
            String virtualNodeName = serverId + "-vnode-" + i;
            int hash = getHash(virtualNodeName);
            ring.put(hash, serverId);
        }
    }
    
    // Removes all virtual nodes for a server from the hash ring
    private void removeVirtualNodes(String serverId, int weight) {
        int numVirtualNodes = weight * VIRTUAL_NODES_PER_WEIGHT;
        
        for (int i = 0; i < numVirtualNodes; i++) {
            String virtualNodeName = serverId + "-vnode-" + i;
            int hash = getHash(virtualNodeName);
            ring.remove(hash);
        }
    }
    
    // Computes the hash for a key
    private int getHash(String key) {
        lock.readLock().lock();
        try {
            md.reset();
            md.update(key.getBytes(StandardCharsets.UTF_8));
            byte[] digest = md.digest();
            
            // Use the first 4 bytes of the digest as an int
            return ((digest[0] & 0xFF) << 24) 
                    | ((digest[1] & 0xFF) << 16) 
                    | ((digest[2] & 0xFF) << 8) 
                    | (digest[3] & 0xFF);
        } finally {
            lock.readLock().unlock();
        }
    }
}