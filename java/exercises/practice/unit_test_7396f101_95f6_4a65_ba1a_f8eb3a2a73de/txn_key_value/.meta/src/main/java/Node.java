import java.util.HashMap;
import java.util.Map;
import java.util.NavigableMap;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Represents a node in the distributed key-value store.
 * Each node stores a subset of the data and participates in the two-phase commit protocol.
 */
public class Node {
    private final int nodeId;
    
    // Value versioning for MVCC: each key maps to a TreeMap of timestamp-to-value mappings
    private final Map<String, NavigableMap<Long, String>> mvccStore = new ConcurrentHashMap<>();
    
    // For the 2PC protocol: transaction ID -> prepared changes
    private final Map<Long, Map<String, String>> preparedWrites = new ConcurrentHashMap<>();
    
    // Lock for synchronizing reads and writes
    private final ReadWriteLock lock = new ReentrantReadWriteLock();

    public Node(int nodeId) {
        this.nodeId = nodeId;
    }

    /**
     * Reads a value for the specified key at the given transaction timestamp.
     * Implements snapshot isolation by returning the latest value as of the transaction's start time.
     */
    public String read(String key, long txTimestamp) {
        lock.readLock().lock();
        try {
            NavigableMap<Long, String> versions = mvccStore.get(key);
            if (versions == null) {
                return null;
            }
            
            // Find the latest version that's less than or equal to txTimestamp
            Map.Entry<Long, String> entry = versions.floorEntry(txTimestamp);
            return entry != null ? entry.getValue() : null;
        } finally {
            lock.readLock().unlock();
        }
    }

    /**
     * Phase 1 of 2PC: prepare the transaction.
     * Returns true if the preparation succeeds, false otherwise.
     */
    public boolean prepare(long txId, Map<String, String> writes) {
        lock.writeLock().lock();
        try {
            // In a real implementation, we would check for conflicts here
            // For simplicity, we'll always succeed in our implementation
            preparedWrites.put(txId, new HashMap<>(writes));
            return true;
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Phase 2 of 2PC: commit the transaction.
     */
    public void commit(long txId) {
        lock.writeLock().lock();
        try {
            Map<String, String> writes = preparedWrites.remove(txId);
            if (writes == null) {
                return; // Transaction was not prepared or already committed/rolled back
            }
            
            // Apply all writes with the transaction timestamp
            for (Map.Entry<String, String> entry : writes.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();
                
                NavigableMap<Long, String> versions = mvccStore.computeIfAbsent(
                    key, k -> new TreeMap<>());
                versions.put(txId, value);
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Phase 2 alternative of 2PC: rollback the transaction.
     */
    public void rollback(long txId) {
        lock.writeLock().lock();
        try {
            preparedWrites.remove(txId);
        } finally {
            lock.writeLock().unlock();
        }
    }

    /**
     * Garbage collect versions older than the provided timestamp.
     */
    public void garbageCollect(long oldestActiveTimestamp) {
        lock.writeLock().lock();
        try {
            for (NavigableMap<Long, String> versions : mvccStore.values()) {
                // Keep at least one version, even if it's older than oldestActiveTimestamp
                if (versions.size() <= 1) {
                    continue;
                }
                
                // Remove versions older than oldestActiveTimestamp, keeping at least the latest
                // one before oldestActiveTimestamp for snapshot isolation
                Long floorKey = versions.floorKey(oldestActiveTimestamp);
                if (floorKey != null) {
                    // Get all keys strictly less than floorKey
                    NavigableMap<Long, String> toRemove = versions.headMap(floorKey, false);
                    toRemove.clear();
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }

    public int getNodeId() {
        return nodeId;
    }
}