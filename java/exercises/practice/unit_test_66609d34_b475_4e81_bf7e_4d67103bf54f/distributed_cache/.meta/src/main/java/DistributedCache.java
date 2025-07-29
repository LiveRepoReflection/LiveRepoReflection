package distributed_cache;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.NavigableMap;
import java.util.TreeMap;

public class DistributedCache {
    private final int replicationFactor;
    private final int perNodeMemoryLimit;
    private final List<Node> nodes;
    private final NavigableMap<Integer, Node> hashRing;
    private int nextNodeId = 0;

    public DistributedCache(int nodeCount, int replicationFactor, int memoryLimit) {
        if (nodeCount < replicationFactor) {
            throw new IllegalArgumentException("Node count must be greater than or equal to replication factor");
        }
        this.replicationFactor = replicationFactor;
        // Each node will have the same memory limit.
        this.perNodeMemoryLimit = memoryLimit;
        nodes = new ArrayList<>();
        hashRing = new TreeMap<>();
        for (int i = 0; i < nodeCount; i++) {
            addNewNode();
        }
    }

    // Adds a new node to the distributed cache.
    public synchronized void addNode() {
        addNewNode();
        rebuildHashRing();
    }

    // Returns the current number of nodes in the cache.
    public synchronized int getNodeCount() {
        return nodes.size();
    }

    // Puts a key-value pair into the cache with specified expiry (in seconds).
    public void put(String key, byte[] value, int expirySeconds) {
        List<Node> replicas = getReplicaNodes(key);
        long currentTime = System.currentTimeMillis();
        long expiryTime = expirySeconds > 0 ? currentTime + expirySeconds * 1000L : Long.MAX_VALUE;
        CacheEntry newEntry = new CacheEntry(value, expiryTime, currentTime);
        for (Node node : replicas) {
            if (node.isAlive()) {
                node.put(key, newEntry);
            }
        }
    }

    // Gets the value for the specified key from the cache.
    public byte[] get(String key) {
        List<Node> replicas = getReplicaNodes(key);
        CacheEntry latestEntry = null;
        boolean found = false;
        for (Node node : replicas) {
            if (!node.isAlive()) {
                continue;
            }
            CacheEntry entry = node.get(key);
            if (entry != null) {
                found = true;
                if (latestEntry == null || entry.version > latestEntry.version) {
                    latestEntry = entry;
                }
            }
        }
        // If we've found a valid entry, perform read repair.
        if (found && latestEntry != null) {
            for (Node node : replicas) {
                if (!node.isAlive())  continue;
                CacheEntry entry = node.get(key);
                if (entry == null || entry.version < latestEntry.version) {
                    node.put(key, latestEntry);
                }
            }
            return latestEntry.value;
        }
        return null;
    }

    // Deletes the key from all relevant replicas.
    public void delete(String key) {
        List<Node> replicas = getReplicaNodes(key);
        for (Node node : replicas) {
            if (node.isAlive()) {
                node.delete(key);
            }
        }
    }

    // Simulates a node failure based on node id.
    public synchronized void simulateNodeFailure(int nodeId) {
        for (Node node : nodes) {
            if (node.getNodeId() == nodeId) {
                node.setAlive(false);
                break;
            }
        }
    }

    // Recovers a failed node.
    public synchronized void recoverNode(int nodeId) {
        for (Node node : nodes) {
            if (node.getNodeId() == nodeId) {
                node.setAlive(true);
                break;
            }
        }
    }

    // Corrupts one replica of a given key by setting its value to corruptValue.
    public void corruptReplica(String key, byte[] corruptValue) {
        List<Node> replicas = getReplicaNodes(key);
        // For simulation, corrupt the first alive replica.
        for (Node node : replicas) {
            if (node.isAlive()) {
                // Create a corrupt entry with a lower version than expected.
                long corruptVersion = System.currentTimeMillis() - 10000; // older version
                CacheEntry corruptEntry = new CacheEntry(corruptValue, Long.MAX_VALUE, corruptVersion);
                node.put(key, corruptEntry);
                break;
            }
        }
    }

    // Helper to add a new node.
    private void addNewNode() {
        Node newNode = new Node(nextNodeId++, perNodeMemoryLimit);
        nodes.add(newNode);
        hashRing.put(hash(Integer.toString(newNode.getNodeId())), newNode);
    }

    // Rebuilds the entire consistent hash ring.
    private synchronized void rebuildHashRing() {
        hashRing.clear();
        for (Node node : nodes) {
            hashRing.put(hash(Integer.toString(node.getNodeId())), node);
        }
    }

    // Gets the replica nodes for a given key using consistent hashing.
    private List<Node> getReplicaNodes(String key) {
        List<Node> replicaNodes = new ArrayList<>();
        if (hashRing.isEmpty()) {
            return replicaNodes;
        }
        int hashKey = hash(key);
        Map.Entry<Integer, Node> entry = hashRing.ceilingEntry(hashKey);
        if (entry == null) {
            entry = hashRing.firstEntry();
        }
        // Traverse the hash ring until we have gathered replicationFactor unique nodes.
        Collection<Node> ringNodes = hashRing.values();
        List<Node> ringList = new ArrayList<>(ringNodes);
        int startIndex = ringList.indexOf(entry.getValue());
        int index = startIndex;
        while (replicaNodes.size() < replicationFactor) {
            Node current = ringList.get(index % ringList.size());
            if (!replicaNodes.contains(current)) {
                replicaNodes.add(current);
            }
            index++;
        }
        return replicaNodes;
    }

    // Simple hash function wrapper.
    private int hash(String key) {
        return Math.abs(key.hashCode());
    }

    // Internal class representing a node in the distributed cache.
    private static class Node {
        private final int nodeId;
        private final int memoryLimit;
        private int currentMemory;
        private volatile boolean alive;
        private final LinkedHashMap<String, CacheEntry> cache;

        public Node(int nodeId, int memoryLimit) {
            this.nodeId = nodeId;
            this.memoryLimit = memoryLimit;
            this.currentMemory = 0;
            this.alive = true;
            // accessOrder true for LRU ordering.
            this.cache = new LinkedHashMap<>(16, 0.75f, true);
        }

        public int getNodeId() {
            return nodeId;
        }

        public boolean isAlive() {
            return alive;
        }

        public void setAlive(boolean status) {
            this.alive = status;
        }

        public synchronized void put(String key, CacheEntry entry) {
            // Remove the old entry if exists.
            CacheEntry old = cache.get(key);
            if (old != null) {
                currentMemory -= old.size;
            }
            // Evict entries if needed.
            while (currentMemory + entry.size > memoryLimit && !cache.isEmpty()) {
                String eldestKey = cache.keySet().iterator().next();
                CacheEntry removed = cache.remove(eldestKey);
                if (removed != null) {
                    currentMemory -= removed.size;
                }
            }
            // Only add if fits, otherwise, skip adding.
            if (entry.size <= memoryLimit) {
                cache.put(key, entry);
                currentMemory += entry.size;
            }
        }

        public synchronized CacheEntry get(String key) {
            CacheEntry entry = cache.get(key);
            if (entry == null) {
                return null;
            }
            long now = System.currentTimeMillis();
            if (entry.expiryTime < now) {
                cache.remove(key);
                currentMemory -= entry.size;
                return null;
            }
            return entry;
        }

        public synchronized void delete(String key) {
            CacheEntry removed = cache.remove(key);
            if (removed != null) {
                currentMemory -= removed.size;
            }
        }
    }

    // Internal class representing a cache entry.
    private static class CacheEntry {
        private final byte[] value;
        private final long expiryTime;
        private final long version;
        private final int size;

        public CacheEntry(byte[] value, long expiryTime, long version) {
            // Copy the content of byte array to avoid external modifications.
            this.value = new byte[value.length];
            System.arraycopy(value, 0, this.value, 0, value.length);
            this.expiryTime = expiryTime;
            this.version = version;
            this.size = value.length;
        }
    }
}