import java.util.concurrent.ConcurrentHashMap;

public class DistributedRateLimiter {

    private static class RateLimitConfig {
        int limit;
        long windowMs;

        RateLimitConfig(int limit, long windowMs) {
            this.limit = limit;
            this.windowMs = windowMs;
        }
    }

    private final ConcurrentHashMap<String, RateLimitConfig> configMap = new ConcurrentHashMap<>();
    private final DistributedKVStore kvStore;

    public DistributedRateLimiter() {
        this.kvStore = new SimpleDistributedKVStore();
    }

    public DistributedRateLimiter(DistributedKVStore kvStore) {
        this.kvStore = kvStore;
    }

    public void setRateLimit(String resource, int limit, long windowMs) {
        configMap.put(resource, new RateLimitConfig(limit, windowMs));
    }

    public boolean isAllowed(String resource, String clientId) {
        RateLimitConfig config = configMap.get(resource);
        if (config == null) {
            throw new IllegalArgumentException("No rate limit configuration for resource: " + resource);
        }

        String key = resource + ":" + clientId;
        long currentCount = kvStore.increment(key, 1, config.windowMs);
        return currentCount <= config.limit;
    }
}