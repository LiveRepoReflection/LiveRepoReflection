import java.util.*;

public class DistributedKeyValueStore {
    private TreeMap<Integer, Node> ring;
    private int replicationFactor;

    public DistributedKeyValueStore() {
        this.replicationFactor = 3;
        ring = new TreeMap<>();
        // Initialize with default nodes
        addNode("node1");
        addNode("node2");
        addNode("node3");
    }

    private int getHash(String key) {
        return Math.abs(key.hashCode());
    }

    private List<Node> getNodesForKey(String key) {
        List<Node> nodes = new ArrayList<>();
        if (ring.isEmpty()) return nodes;
        int hash = getHash(key);
        SortedMap<Integer, Node> tailMap = ring.tailMap(hash);
        Iterator<Node> it = tailMap.values().iterator();
        while (it.hasNext() && nodes.size() < replicationFactor) {
            nodes.add(it.next());
        }
        if (nodes.size() < replicationFactor) {
            for (Node node : ring.values()) {
                if (nodes.size() < replicationFactor) {
                    nodes.add(node);
                } else {
                    break;
                }
            }
        }
        return nodes;
    }

    public synchronized boolean put(String key, String value) {
        if (key == null || key.isEmpty() || value == null) {
            return false;
        }
        List<Node> nodes = getNodesForKey(key);
        if (nodes.isEmpty()) return false;
        for (Node node : nodes) {
            node.put(key, value);
        }
        return true;
    }

    public synchronized String get(String key) {
        if (key == null || key.isEmpty()) return null;
        List<Node> nodes = getNodesForKey(key);
        if (nodes.isEmpty()) return null;
        // Retrieve value from the primary node for strong consistency
        return nodes.get(0).get(key);
    }

    public synchronized boolean delete(String key) {
        if (key == null || key.isEmpty()) return false;
        List<Node> nodes = getNodesForKey(key);
        if (nodes.isEmpty()) return false;
        boolean success = true;
        for (Node node : nodes) {
            success = node.delete(key) && success;
        }
        return success;
    }

    public synchronized void addNode(String nodeId) {
        if (nodeId == null || nodeId.isEmpty()) return;
        int hash = getHash(nodeId);
        // Ensure uniqueness in the ring; if collision, adjust hash by appending nano time
        if (ring.containsKey(hash)) {
            hash = getHash(nodeId + System.nanoTime());
        }
        Node newNode = new Node(nodeId);
        ring.put(hash, newNode);
        rebalanceAll();
    }

    public synchronized void removeNode(String nodeId) {
        if (nodeId == null || nodeId.isEmpty()) return;
        Integer keyToRemove = null;
        for (Map.Entry<Integer, Node> entry : ring.entrySet()) {
            if (entry.getValue().id.equals(nodeId)) {
                keyToRemove = entry.getKey();
                break;
            }
        }
        if (keyToRemove != null) {
            ring.remove(keyToRemove);
            rebalanceAll();
        }
    }

    public synchronized List<String> getActiveNodeIds() {
        List<String> active = new ArrayList<>();
        for (Node node : ring.values()) {
            active.add(node.id);
        }
        return active;
    }

    private void rebalanceAll() {
        // Gather all keys and values from all nodes in the current cluster.
        Map<String, String> allData = new HashMap<>();
        for (Node node : ring.values()) {
            allData.putAll(node.getAllData());
        }
        // Clear each node data before rebalancing.
        for (Node node : ring.values()) {
            node.clearStore();
        }
        // Reinsert keys based on the current hash ring distribution.
        for (Map.Entry<String, String> entry : allData.entrySet()) {
            List<Node> nodes = getNodesForKey(entry.getKey());
            for (Node node : nodes) {
                node.put(entry.getKey(), entry.getValue());
            }
        }
    }

    // Inner Node class simulating a physical node in the system
    private static class Node {
        private String id;
        private Map<String, String> store;

        public Node(String id) {
            this.id = id;
            this.store = new HashMap<>();
        }

        public synchronized void put(String key, String value) {
            store.put(key, value);
        }

        public synchronized String get(String key) {
            return store.get(key);
        }

        public synchronized boolean delete(String key) {
            return store.remove(key) != null;
        }

        public synchronized Map<String, String> getAllData() {
            return new HashMap<>(store);
        }

        public synchronized void clearStore() {
            store.clear();
        }
    }
}