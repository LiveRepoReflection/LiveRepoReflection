import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class ConsistentStore {
    private final int replicationFactor;
    private final int virtualNodes;
    private final SortedMap<Integer, Node> ring;
    private final Map<String, Node> nodes;

    public ConsistentStore(int replicationFactor, int virtualNodes) {
        this.replicationFactor = replicationFactor;
        this.virtualNodes = virtualNodes;
        this.ring = new TreeMap<>();
        this.nodes = new ConcurrentHashMap<>();
    }

    // Adds a new physical node with the provided nodeName and virtual nodes.
    public synchronized void addNode(String nodeName) {
        if (nodes.containsKey(nodeName)) {
            return;
        }
        Node node = new Node(nodeName);
        nodes.put(nodeName, node);
        for (int i = 0; i < virtualNodes; i++) {
            int hash = computeHash(nodeName + "#" + i);
            ring.put(hash, node);
        }
    }

    // Removes a physical node and its virtual nodes from the ring.
    public synchronized void removeNode(String nodeName) {
        Node node = nodes.remove(nodeName);
        if (node == null) {
            return;
        }
        Iterator<Map.Entry<Integer, Node>> iterator = ring.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<Integer, Node> entry = iterator.next();
            if (entry.getValue().getName().equals(nodeName)) {
                iterator.remove();
            }
        }
    }

    // Marks the node as failed (unavailable).
    public synchronized void failNode(String nodeName) {
        Node node = nodes.get(nodeName);
        if (node != null) {
            node.setAvailable(false);
        }
    }

    // Recovers a failed node.
    public synchronized void recoverNode(String nodeName) {
        Node node = nodes.get(nodeName);
        if (node != null) {
            node.setAvailable(true);
        }
    }

    // Stores the key-value pair on all replicas.
    public synchronized void put(String key, String value) {
        List<Node> replicas = getReplicaNodes(key);
        int availableCount = countAvailable(replicas);
        if (availableCount < quorum()) {
            throw new RuntimeException("Insufficient replicas available");
        }
        for (Node node : replicas) {
            if (node.isAvailable()) {
                node.put(key, value);
            }
        }
    }

    // Retrieves the value for the key using quorum based reads.
    public synchronized String get(String key) {
        List<Node> replicas = getReplicaNodes(key);
        int availableCount = countAvailable(replicas);
        if (availableCount < quorum()) {
            throw new RuntimeException("Insufficient replicas available");
        }
        // For strong consistency, assume all available replicas hold the same value.
        for (Node node : replicas) {
            if (node.isAvailable()) {
                return node.get(key);
            }
        }
        return null;
    }

    // Deletes the key from all replicas.
    public synchronized boolean delete(String key) {
        List<Node> replicas = getReplicaNodes(key);
        int availableCount = countAvailable(replicas);
        if (availableCount < quorum()) {
            throw new RuntimeException("Insufficient replicas available");
        }
        boolean deleted = false;
        for (Node node : replicas) {
            if (node.isAvailable()) {
                deleted = node.delete(key) || deleted;
            }
        }
        return deleted;
    }

    // Shuts down the store: clears all data. In a real system, cleanup would be more extensive.
    public synchronized void shutdown() {
        ring.clear();
        nodes.clear();
    }

    // Returns the list of replica nodes responsible for storing the key.
    private List<Node> getReplicaNodes(String key) {
        List<Node> result = new ArrayList<>();
        if (ring.isEmpty()) {
            return result;
        }
        int hash = computeHash(key);
        SortedMap<Integer, Node> tailMap = ring.tailMap(hash);
        Iterator<Node> iterator = tailMap.values().iterator();
        // Use a set to maintain uniqueness of physical nodes.
        Set<String> added = new HashSet<>();
        while (iterator.hasNext() && result.size() < replicationFactor) {
            Node node = iterator.next();
            if (!added.contains(node.getName())) {
                result.add(node);
                added.add(node.getName());
            }
        }
        if (result.size() < replicationFactor) {
            iterator = ring.values().iterator();
            while (iterator.hasNext() && result.size() < replicationFactor) {
                Node node = iterator.next();
                if (!added.contains(node.getName())) {
                    result.add(node);
                    added.add(node.getName());
                }
            }
        }
        return result;
    }

    // Computes a non-negative hash from the given key.
    private int computeHash(String key) {
        int hash = key.hashCode();
        return hash & 0x7fffffff;
    }

    // Returns the required quorum count.
    private int quorum() {
        return (replicationFactor / 2) + 1;
    }

    // Counts the available nodes in the list.
    private int countAvailable(List<Node> nodes) {
        int count = 0;
        for (Node node : nodes) {
            if (node.isAvailable()) {
                count++;
            }
        }
        return count;
    }

    // Inner class representing a node in the consistent store.
    private static class Node {
        private final String name;
        private volatile boolean available;
        private final Map<String, String> data;

        public Node(String name) {
            this.name = name;
            this.available = true;
            this.data = new ConcurrentHashMap<>();
        }

        public String getName() {
            return name;
        }

        public boolean isAvailable() {
            return available;
        }

        public void setAvailable(boolean available) {
            this.available = available;
        }

        public void put(String key, String value) {
            data.put(key, value);
        }

        public String get(String key) {
            return data.get(key);
        }

        public boolean delete(String key) {
            return data.remove(key) != null;
        }
    }
}