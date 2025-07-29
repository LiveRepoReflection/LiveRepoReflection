import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;

public class ConsistentHashingLoadBalancer {

    private final int virtualNodesCount;
    private final TreeMap<Integer, String> ring;
    private final Map<String, List<Integer>> nodeToHashes;
    private final MessageDigest digest;

    public ConsistentHashingLoadBalancer(int virtualNodesCount) {
        if (virtualNodesCount <= 0) {
            throw new IllegalArgumentException("virtualNodesCount must be positive");
        }
        this.virtualNodesCount = virtualNodesCount;
        this.ring = new TreeMap<>();
        this.nodeToHashes = new HashMap<>();
        try {
            // Using SHA-256 for generating hash values.
            this.digest = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            // Should not occur as SHA-256 is standard
            throw new RuntimeException("SHA-256 algorithm not found", e);
        }
    }

    public synchronized void addNode(String nodeId) {
        if (nodeId == null || nodeId.isEmpty()) {
            throw new IllegalArgumentException("nodeId cannot be null or empty");
        }
        // If node is already added, do not add again.
        if (nodeToHashes.containsKey(nodeId)) {
            return;
        }
        List<Integer> hashes = new ArrayList<>();
        for (int i = 0; i < virtualNodesCount; i++) {
            String replicaId = nodeId + "-" + i;
            int hash = computeHash(replicaId);
            ring.put(hash, nodeId);
            hashes.add(hash);
        }
        nodeToHashes.put(nodeId, hashes);
    }

    public synchronized void removeNode(String nodeId) {
        if (nodeId == null || nodeId.isEmpty()) {
            throw new IllegalArgumentException("nodeId cannot be null or empty");
        }
        List<Integer> hashes = nodeToHashes.get(nodeId);
        if (hashes == null) {
            return; // Node not present in the ring
        }
        for (Integer hash : hashes) {
            ring.remove(hash);
        }
        nodeToHashes.remove(nodeId);
    }

    public synchronized String getNode(String key) {
        if (key == null) {
            throw new IllegalArgumentException("key cannot be null");
        }
        if (ring.isEmpty()) {
            return null;
        }
        int hash = computeHash(key);
        Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            // wrap-around to the first entry if no entry is found for the given hash
            entry = ring.firstEntry();
        }
        return entry.getValue();
    }

    public synchronized int getRingSize() {
        return ring.size();
    }

    /**
     * Computes a 32-bit hash value for the given string using SHA-256.
     */
    private int computeHash(String input) {
        byte[] hashBytes;
        synchronized (digest) {
            digest.reset();
            digest.update(input.getBytes());
            hashBytes = digest.digest();
        }
        // Use the first 4 bytes to form a 32-bit integer hash (big-endian)
        ByteBuffer buffer = ByteBuffer.wrap(hashBytes);
        buffer.order(ByteOrder.BIG_ENDIAN);
        return buffer.getInt();
    }
}