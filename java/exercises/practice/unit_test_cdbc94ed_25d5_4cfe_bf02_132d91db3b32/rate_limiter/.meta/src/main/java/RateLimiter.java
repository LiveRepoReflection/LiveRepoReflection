import java.util.concurrent.ConcurrentHashMap;

public class RateLimiter {

    private final ConfigurationService configurationService;
    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();

    public RateLimiter(ConfigurationService configurationService) {
        this.configurationService = configurationService;
    }

    public boolean allowRequest(String clientId) {
        RateLimitConfiguration config = configurationService.getConfiguration(clientId);
        if (config == null) {
            return false;
        }
        Bucket bucket = buckets.computeIfAbsent(clientId,
                id -> new Bucket(config.getLimit(), config.getTimeWindowMillis()));
        synchronized (bucket) {
            long now = System.currentTimeMillis();
            if (now - bucket.windowStart >= bucket.timeWindowMillis) {
                bucket.windowStart = now;
                bucket.availableTokens = bucket.capacity;
            }
            if (bucket.availableTokens > 0) {
                bucket.availableTokens--;
                return true;
            } else {
                return false;
            }
        }
    }

    private static class Bucket {
        final int capacity;
        final long timeWindowMillis;
        long windowStart;
        int availableTokens;

        Bucket(int capacity, long timeWindowMillis) {
            this.capacity = capacity;
            this.timeWindowMillis = timeWindowMillis;
            this.windowStart = System.currentTimeMillis();
            this.availableTokens = capacity;
        }
    }
}