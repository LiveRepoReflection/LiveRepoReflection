/**
 * Interface for a distributed cache to be used by the rate limiter.
 * Implementations can use Redis, Memcached, or other distributed caching systems.
 */
public interface DistributedCache {
    
    /**
     * Gets a rate limit rule by its ID.
     *
     * @param ruleId The unique identifier of the rule.
     * @return The rate limit rule, or null if it doesn't exist.
     */
    RateLimitRule getRule(String ruleId);
    
    /**
     * Sets a rate limit rule in the cache.
     *
     * @param ruleId The unique identifier of the rule.
     * @param rule The rule to store.
     */
    void setRule(String ruleId, RateLimitRule rule);
    
    /**
     * Checks if a rule exists in the cache.
     *
     * @param ruleId The unique identifier of the rule.
     * @return true if the rule exists, false otherwise.
     */
    boolean ruleExists(String ruleId);
    
    /**
     * Updates an existing rate limit rule in the cache.
     *
     * @param ruleId The unique identifier of the rule.
     * @param limit The new request limit.
     * @param window The new time window in seconds.
     */
    void updateRule(String ruleId, int limit, int window);
    
    /**
     * Removes a rate limit rule from the cache.
     *
     * @param ruleId The unique identifier of the rule to remove.
     */
    void removeRule(String ruleId);
    
    /**
     * Atomically increments the request count for the given target and rule.
     * This operation must be atomic to ensure correct rate limiting behavior.
     *
     * @param targetId The identifier of the target (user or service).
     * @param ruleId The identifier of the rule being applied.
     * @return The new count after incrementing.
     */
    int incrementRequestCount(String targetId, String ruleId);
    
    /**
     * Decrements the request count for the given target and rule.
     * This is used when a request is initially counted but then rejected.
     *
     * @param targetId The identifier of the target (user or service).
     * @param ruleId The identifier of the rule being applied.
     */
    void decrementRequestCount(String targetId, String ruleId);
}