import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class RateLimiter {
    private final TimeProvider timeProvider;
    private final Map<String, TokenBucket> buckets;
    private final Map<String, String> userTiers;
    private final Map<String, Integer> apiPriorities;
    
    private static final int DEFAULT_CAPACITY = 100;
    private static final int DEFAULT_REFILL_RATE = 100;
    private static final long WINDOW_SIZE_MS = 60_000; // 1 minute

    public RateLimiter(TimeProvider timeProvider) {
        this.timeProvider = timeProvider;
        this.buckets = new ConcurrentHashMap<>();
        this.userTiers = new ConcurrentHashMap<>();
        this.apiPriorities = new ConcurrentHashMap<>();
    }

    public boolean isAllowed(String userId, String apiId) {
        String key = generateKey(userId, apiId);
        TokenBucket bucket = buckets.computeIfAbsent(key, k -> createBucket(userId, apiId));
        return bucket.tryConsume();
    }

    public void setUserTier(String userId, String tier) {
        userTiers.put(userId, tier);
        // Reset existing buckets for this user
        buckets.entrySet().removeIf(entry -> entry.getKey().startsWith(userId + ":"));
    }

    public void setPriority(String apiId, int priority) {
        apiPriorities.put(apiId, priority);
        // Reset existing buckets for this API
        buckets.entrySet().removeIf(entry -> entry.getKey().contains(":" + apiId));
    }

    private TokenBucket createBucket(String userId, String apiId) {
        int capacity = calculateCapacity(userId);
        int refillRate = calculateRefillRate(apiId);
        return new TokenBucket(capacity, refillRate, timeProvider);
    }

    private int calculateCapacity(String userId) {
        String tier = userTiers.getOrDefault(userId, "BASIC");
        switch (tier) {
            case "PREMIUM":
                return DEFAULT_CAPACITY * 2;
            case "ENTERPRISE":
                return DEFAULT_CAPACITY * 5;
            default:
                return DEFAULT_CAPACITY;
        }
    }

    private int calculateRefillRate(String apiId) {
        int priority = apiPriorities.getOrDefault(apiId, 3);
        return DEFAULT_REFILL_RATE / priority;
    }

    private String generateKey(String userId, String apiId) {
        return userId + ":" + apiId;
    }

    private class TokenBucket {
        private final int capacity;
        private final int refillRate;
        private final TimeProvider timeProvider;
        private double tokens;
        private long lastRefillTimestamp;

        public TokenBucket(int capacity, int refillRate, TimeProvider timeProvider) {
            this.capacity = capacity;
            this.refillRate = refillRate;
            this.timeProvider = timeProvider;
            this.tokens = capacity;
            this.lastRefillTimestamp = timeProvider.getCurrentTimeMillis();
        }

        public synchronized boolean tryConsume() {
            refill();
            if (tokens >= 1) {
                tokens--;
                return true;
            }
            return false;
        }

        private void refill() {
            long now = timeProvider.getCurrentTimeMillis();
            long timePassed = now - lastRefillTimestamp;
            
            if (timePassed > WINDOW_SIZE_MS) {
                // Reset if window has passed
                tokens = capacity;
                lastRefillTimestamp = now;
                return;
            }

            // Calculate tokens to add based on time passed
            double tokensToAdd = (timePassed / 1000.0) * refillRate;
            tokens = Math.min(capacity, tokens + tokensToAdd);
            lastRefillTimestamp = now;
        }
    }
}