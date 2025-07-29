import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DistributedConsistentCache {
    private ConsistentHashRing hashRing;
    private int replicationFactor;
    private ExecutorService executor;

    public DistributedConsistentCache(List<CacheNode> nodes, int replicationFactor) {
        this.replicationFactor = replicationFactor;
        this.hashRing = new ConsistentHashRing(nodes);
        this.executor = Executors.newCachedThreadPool();
    }

    public void put(String key, byte[] value) {
        CacheNode primary = hashRing.getPrimaryNode(key);
        if (primary != null) {
            primary.put(key, value);
            // Asynchronously replicate to additional nodes
            List<CacheNode> replicas = hashRing.getReplicas(key, replicationFactor);
            replicas.remove(primary);
            for (CacheNode replica : replicas) {
                executor.submit(() -> {
                    try {
                        Thread.sleep(50);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    replica.put(key, value);
                });
            }
        }
    }

    public byte[] get(String key) {
        CacheNode primary = hashRing.getPrimaryNode(key);
        if (primary != null) {
            CacheNode.ValueWrapper wrapper = primary.get(key);
            if (wrapper != null) {
                return wrapper.getValue();
            }
        }
        // Check replicas if primary miss occurs
        List<CacheNode> replicas = hashRing.getReplicas(key, replicationFactor);
        for (CacheNode replica : replicas) {
            CacheNode.ValueWrapper wrapper = replica.get(key);
            if (wrapper != null) {
                return wrapper.getValue();
            }
        }
        return null;
    }

    public void removeNode(String nodeId) {
        // Mark node as unavailable and remove it from the hash ring
        for (CacheNode node : hashRing.getAllNodes()) {
            if (node.getNodeId().equals(nodeId)) {
                node.setAvailable(false);
                break;
            }
        }
        hashRing.removeNode(nodeId);
    }

    public String getPrimaryNodeIdForKey(String key) {
        CacheNode primary = hashRing.getPrimaryNode(key);
        return primary != null ? primary.getNodeId() : null;
    }

    public void shutdown() {
        executor.shutdown();
    }
}