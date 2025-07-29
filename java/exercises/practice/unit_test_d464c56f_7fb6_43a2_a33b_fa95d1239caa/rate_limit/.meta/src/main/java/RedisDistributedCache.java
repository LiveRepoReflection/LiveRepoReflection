import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Implementation of the DistributedCache interface using Redis.
 * This is a simplified version for demonstration purposes.
 * In a real-world scenario, you would use a Redis client like Jedis or Lettuce.
 */
public class RedisDistributedCache implements DistributedCache {
    private final Map<String, RateLimitRule> rules = new ConcurrentHashMap<>();
    private final Map<String, AtomicInteger> requestCounts = new ConcurrentHashMap<>();
    private final Map<String, Long> expirationTimes = new ConcurrentHashMap<>();
    private final int defaultExpirationSeconds;
    
    /**
     * Constructs a new RedisDistributedCache with the given expiration time.
     *
     * @param defaultExpirationSeconds The default expiration time for rate limit records in seconds.
     */
    public RedisDistributedCache(int defaultExpirationSeconds) {
        this.defaultExpirationSeconds = defaultExpirationSeconds;
    }
    
    @Override
    public RateLimitRule getRule(String ruleId) {
        cleanupExpiredEntries();
        return rules.get(ruleId);
    }
    
    @Override
    public void setRule(String ruleId, RateLimitRule rule) {
        rules.put(ruleId, rule);
    }
    
    @Override
    public boolean ruleExists(String ruleId) {
        return rules.containsKey(ruleId);
    }
    
    @Override
    public void updateRule(String ruleId, int limit, int window) {
        RateLimitRule oldRule = rules.get(ruleId);
        if (oldRule != null) {
            RateLimitRule newRule = new RateLimitRule(ruleId, oldRule.getTarget(), limit, window);
            rules.put(ruleId, newRule);
        }
    }
    
    @Override
    public void removeRule(String ruleId) {
        rules.remove(ruleId);
        
        // Remove all request counters associated with this rule
        requestCounts.entrySet().removeIf(entry -> entry.getKey().endsWith(":" + ruleId));
        expirationTimes.entrySet().removeIf(entry -> entry.getKey().endsWith(":" + ruleId));
    }
    
    @Override
    public synchronized int incrementRequestCount(String targetId, String ruleId) {
        cleanupExpiredEntries();
        
        String key = targetId + ":" + ruleId;
        AtomicInteger counter = requestCounts.computeIfAbsent(key, k -> new AtomicInteger(0));
        
        // Set or update the expiration time
        expirationTimes.put(key, System.currentTimeMillis() + (defaultExpirationSeconds * 1000L));
        
        return counter.incrementAndGet();
    }
    
    @Override
    public synchronized void decrementRequestCount(String targetId, String ruleId) {
        String key = targetId + ":" + ruleId;
        AtomicInteger counter = requestCounts.get(key);
        
        if (counter != null && counter.get() > 0) {
            counter.decrementAndGet();
        }
    }
    
    /**
     * Cleans up expired entries from the cache.
     * This method should be called periodically to prevent memory leaks.
     */
    private void cleanupExpiredEntries() {
        long currentTime = System.currentTimeMillis();
        
        expirationTimes.entrySet().removeIf(entry -> {
            if (entry.getValue() < currentTime) {
                String key = entry.getKey();
                requestCounts.remove(key);
                return true;
            }
            return false;
        });
    }
}