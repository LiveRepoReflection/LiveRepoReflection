/**
 * A distributed rate limiter that enforces request rate limits
 * across multiple servers in a distributed environment.
 */
public class DistributedRateLimiter {
    private final DistributedCache cache;
    
    /**
     * Constructs a new DistributedRateLimiter with the given configuration.
     *
     * @param config The configuration for the rate limiter.
     */
    public DistributedRateLimiter(RateLimiterConfig config) {
        this.cache = config.getCache();
    }
    
    /**
     * Adds a new rate limiting rule.
     *
     * @param ruleId The unique identifier for the rule.
     * @param target The target (user ID, service ID, or "*" for wildcard) this rule applies to.
     * @param limit The maximum number of requests allowed in the time window.
     * @param window The time window in seconds.
     */
    public void addRule(String ruleId, String target, int limit, int window) {
        RateLimitRule rule = new RateLimitRule(ruleId, target, limit, window);
        cache.setRule(ruleId, rule);
    }
    
    /**
     * Updates an existing rate limiting rule.
     *
     * @param ruleId The unique identifier of the rule to update.
     * @param limit The new request limit.
     * @param window The new time window in seconds.
     * @return true if the rule was updated, false if the rule doesn't exist.
     */
    public boolean updateRule(String ruleId, int limit, int window) {
        if (!cache.ruleExists(ruleId)) {
            return false;
        }
        
        cache.updateRule(ruleId, limit, window);
        return true;
    }
    
    /**
     * Removes a rate limiting rule.
     *
     * @param ruleId The unique identifier of the rule to remove.
     * @return true if the rule was removed, false if the rule doesn't exist.
     */
    public boolean removeRule(String ruleId) {
        if (!cache.ruleExists(ruleId)) {
            return false;
        }
        
        cache.removeRule(ruleId);
        return true;
    }
    
    /**
     * Checks if a request from the given target ID is allowed based on the specified rule ID.
     * This method atomically updates the request count in the cache if the request is allowed.
     *
     * @param targetId The identifier of the requester (user ID or service ID).
     * @param ruleId The identifier of the rule to apply.
     * @return true if the request is allowed, false otherwise.
     */
    public boolean isAllowed(String targetId, String ruleId) {
        // Get the rule from the cache
        RateLimitRule rule = cache.getRule(ruleId);
        
        // If the rule doesn't exist, deny the request
        if (rule == null) {
            return false;
        }
        
        // Check if the target matches the rule's target or if the rule has a wildcard target
        if (!rule.getTarget().equals("*") && !rule.getTarget().equals(targetId)) {
            return false;
        }
        
        // Atomically increment the request count and check if it exceeds the limit
        int count = cache.incrementRequestCount(targetId, ruleId);
        
        // If the request count exceeds the limit, decrement it and deny the request
        if (count > rule.getLimit()) {
            cache.decrementRequestCount(targetId, ruleId);
            return false;
        }
        
        // The request is allowed
        return true;
    }
}