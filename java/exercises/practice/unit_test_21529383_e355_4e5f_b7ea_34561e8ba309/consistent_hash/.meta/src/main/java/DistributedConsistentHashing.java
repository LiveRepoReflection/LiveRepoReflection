import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.ThreadLocalRandom;

public class DistributedConsistentHashing {

    // TreeMap to represent the hash ring, key is the node's hash, value is the Node object.
    private final TreeMap<Long, Node> ring = new TreeMap<>();
    // Map to keep track of nodes by their id.
    private final Map<Integer, Node> idToNode = new HashMap<>();
    // Counter to assign unique node IDs.
    private int nodeIdCounter = 0;
    // Lock for thread safety.
    private final ReentrantLock lock = new ReentrantLock();
    // Maximum value for the hash space (2^32 - 1).
    private final long MAX_HASH = ((long) 1 << 32) - 1;

    // Private static inner class representing a node in the distributed system.
    private static class Node {
        final int id;
        final long hash;
        // Each node maintains its own local key-value store.
        final Map<String, String> storage;

        Node(int id, long hash) {
            this.id = id;
            this.hash = hash;
            this.storage = new ConcurrentHashMap<>();
        }
    }

    // Constructor to initialize the system with numNodes nodes.
    public DistributedConsistentHashing(int numNodes) {
        for (int i = 0; i < numNodes; i++) {
            addNodeInternal();
        }
    }

    // Stores the value associated with the key in the appropriate node.
    public void put(String key, String value) {
        lock.lock();
        try {
            long keyHash = hashKey(key);
            Node node = getNodeForKey(keyHash);
            node.storage.put(key, value);
        } finally {
            lock.unlock();
        }
    }

    // Retrieves the value associated with the key from the responsible node.
    public String get(String key) {
        lock.lock();
        try {
            long keyHash = hashKey(key);
            Node node = getNodeForKey(keyHash);
            return node.storage.get(key);
        } finally {
            lock.unlock();
        }
    }

    // Adds a new node to the system and migrates keys from its successor as necessary.
    public int addNode() {
        lock.lock();
        try {
            Node newNode = addNodeInternal();
            // After adding, determine the successor of the new node.
            Node successor = getSuccessor(newNode.hash);
            if (successor != null && successor != newNode) {
                // Transfer keys from the successor that should now be handled by the new node.
                List<String> keysToTransfer = new ArrayList<>();
                for (String key : successor.storage.keySet()) {
                    long keyHash = hashKey(key);
                    Node responsible = getNodeForHash(keyHash, ring);
                    if (responsible.id == newNode.id) {
                        keysToTransfer.add(key);
                    }
                }
                for (String key : keysToTransfer) {
                    String val = successor.storage.remove(key);
                    newNode.storage.put(key, val);
                }
            }
            return newNode.id;
        } finally {
            lock.unlock();
        }
    }

    // Removes the node with the given nodeId and transfers its keys to its successor.
    public void removeNode(int nodeId) {
        lock.lock();
        try {
            Node node = idToNode.get(nodeId);
            if (node == null) {
                return;
            }
            // Remove the node from the ring and the id mapping.
            ring.remove(node.hash);
            idToNode.remove(nodeId);

            // Find the successor to receive the removed node's keys.
            Node successor = getSuccessor(node.hash);
            if (successor == null) {
                return;
            }
            for (Map.Entry<String, String> entry : node.storage.entrySet()) {
                successor.storage.put(entry.getKey(), entry.getValue());
            }
        } finally {
            lock.unlock();
        }
    }

    // Rebalances the entire system by gathering all keys and reassigning them to the appropriate nodes.
    public void rebalance() {
        lock.lock();
        try {
            Map<String, String> allData = new HashMap<>();
            for (Node node : ring.values()) {
                allData.putAll(node.storage);
                node.storage.clear();
            }
            for (Map.Entry<String, String> entry : allData.entrySet()) {
                long keyHash = hashKey(entry.getKey());
                Node node = getNodeForKey(keyHash);
                node.storage.put(entry.getKey(), entry.getValue());
            }
        } finally {
            lock.unlock();
        }
    }

    // Helper method to add a node internally without external locking.
    private Node addNodeInternal() {
        long nodeHash = generateRandomHash();
        // Ensure unique hash value on the ring.
        while (ring.containsKey(nodeHash)) {
            nodeHash = generateRandomHash();
        }
        int nodeId = nodeIdCounter++;
        Node newNode = new Node(nodeId, nodeHash);
        ring.put(nodeHash, newNode);
        idToNode.put(nodeId, newNode);
        return newNode;
    }

    // Generates a random hash value within the allowed range.
    private long generateRandomHash() {
        return ThreadLocalRandom.current().nextLong(0, MAX_HASH + 1);
    }

    // Computes the hash for a given key.
    private long hashKey(String key) {
        return ((long) key.hashCode() & 0xffffffffL) % (MAX_HASH + 1);
    }

    // Determines the node responsible for the given keyHash using the current ring.
    private Node getNodeForKey(long keyHash) {
        return getNodeForHash(keyHash, ring);
    }

    // Retrieves the node in the provided ring that is responsible for the keyHash.
    private Node getNodeForHash(long keyHash, TreeMap<Long, Node> ringMap) {
        Map.Entry<Long, Node> entry = ringMap.ceilingEntry(keyHash);
        if (entry == null) {
            return ringMap.firstEntry().getValue();
        }
        return entry.getValue();
    }

    // Gets the successor node following the given hash in the ring.
    private Node getSuccessor(long hash) {
        Map.Entry<Long, Node> entry = ring.higherEntry(hash);
        if (entry == null) {
            return ring.firstEntry().getValue();
        }
        return entry.getValue();
    }
}