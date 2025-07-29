import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

public class ConsistentHashRing {
    private TreeMap<Integer, CacheNode> ring;
    private List<CacheNode> nodes;

    public ConsistentHashRing(List<CacheNode> nodes) {
        this.nodes = new ArrayList<>();
        this.ring = new TreeMap<>();
        for (CacheNode node : nodes) {
            addNode(node);
        }
    }

    private int hash(String key) {
        return Math.abs(key.hashCode());
    }

    public synchronized void addNode(CacheNode node) {
        int hash = hash(node.getNodeId());
        ring.put(hash, node);
        nodes.add(node);
    }

    public synchronized void removeNode(String nodeId) {
        int hash = hash(nodeId);
        ring.remove(hash);
        nodes.removeIf(n -> n.getNodeId().equals(nodeId));
    }

    public synchronized CacheNode getPrimaryNode(String key) {
        if (ring.isEmpty()) {
            return null;
        }
        int hashKey = hash(key);
        SortedMap<Integer, CacheNode> tailMap = ring.tailMap(hashKey);
        int nodeHash = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();
        CacheNode candidate = ring.get(nodeHash);
        if (candidate.isAvailable()) {
            return candidate;
        } else {
            for (CacheNode node : ring.values()) {
                if (node.isAvailable()) {
                    return node;
                }
            }
            return null;
        }
    }

    public synchronized List<CacheNode> getReplicas(String key, int replicationFactor) {
        List<CacheNode> replicas = new ArrayList<>();
        if (ring.isEmpty()) {
            return replicas;
        }
        int hashKey = hash(key);
        SortedMap<Integer, CacheNode> tailMap = ring.tailMap(hashKey);
        Iterator<CacheNode> it = tailMap.values().iterator();
        while (it.hasNext() && replicas.size() < replicationFactor) {
            CacheNode node = it.next();
            if (node.isAvailable() && !replicas.contains(node)) {
                replicas.add(node);
            }
        }
        if (replicas.size() < replicationFactor) {
            for (CacheNode node : ring.values()) {
                if (replicas.size() >= replicationFactor) {
                    break;
                }
                if (node.isAvailable() && !replicas.contains(node)) {
                    replicas.add(node);
                }
            }
        }
        return replicas;
    }

    public synchronized List<CacheNode> getAllNodes() {
        return new ArrayList<>(nodes);
    }
}