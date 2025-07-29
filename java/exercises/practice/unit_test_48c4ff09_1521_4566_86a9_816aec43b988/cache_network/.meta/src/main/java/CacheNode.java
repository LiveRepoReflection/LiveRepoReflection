import java.util.LinkedHashMap;
import java.util.Map;

public class CacheNode {
    private final int capacity;
    private final Map<Integer, Integer> cache;
    private final int nodeId;
    
    public CacheNode(int capacity, int nodeId) {
        this.capacity = capacity;
        this.nodeId = nodeId;
        this.cache = new LinkedHashMap<Integer, Integer>(capacity, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<Integer, Integer> eldest) {
                return size() > capacity;
            }
        };
    }
    
    public int processRequest(int item, int originLatency) {
        if (cache.containsKey(item)) {
            return 0; // Cache hit - no additional latency
        } else {
            cache.put(item, item);
            return originLatency; // Cache miss - add origin latency
        }
    }
    
    public int getNodeId() {
        return nodeId;
    }
}