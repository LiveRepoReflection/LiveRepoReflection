import java.util.concurrent.ConcurrentHashMap;

public class CacheNode {
    private String nodeId;
    private volatile boolean available;
    private ConcurrentHashMap<String, ValueWrapper> store;

    public CacheNode(String nodeId) {
        this.nodeId = nodeId;
        this.available = true;
        this.store = new ConcurrentHashMap<>();
    }

    public String getNodeId() {
        return nodeId;
    }

    public boolean isAvailable() {
        return available;
    }

    public void setAvailable(boolean available) {
        this.available = available;
    }

    public synchronized void put(String key, byte[] value) {
        long timestamp = System.currentTimeMillis();
        store.put(key, new ValueWrapper(value, timestamp));
    }

    public synchronized ValueWrapper get(String key) {
        return store.get(key);
    }

    public static class ValueWrapper {
        private byte[] value;
        private long timestamp;

        public ValueWrapper(byte[] value, long timestamp) {
            this.value = value;
            this.timestamp = timestamp;
        }

        public byte[] getValue() {
            return value;
        }

        public long getTimestamp() {
            return timestamp;
        }
    }
}