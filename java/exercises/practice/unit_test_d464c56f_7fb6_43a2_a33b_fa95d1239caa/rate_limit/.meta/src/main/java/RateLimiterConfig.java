/**
 * Configuration for the DistributedRateLimiter.
 * Contains settings for cache connection and other parameters.
 */
public class RateLimiterConfig {
    private DistributedCache cache;
    private int defaultExpirationSeconds = 3600; // Default expiration time (1 hour)
    
    /**
     * Gets the distributed cache implementation to use.
     *
     * @return The distributed cache.
     */
    public DistributedCache getCache() {
        return cache;
    }
    
    /**
     * Sets the distributed cache implementation to use.
     *
     * @param cache The distributed cache.
     */
    public void setCache(DistributedCache cache) {
        this.cache = cache;
    }
    
    /**
     * Gets the default expiration time for rate limit records in seconds.
     *
     * @return The default expiration time in seconds.
     */
    public int getDefaultExpirationSeconds() {
        return defaultExpirationSeconds;
    }
    
    /**
     * Sets the default expiration time for rate limit records in seconds.
     *
     * @param defaultExpirationSeconds The default expiration time in seconds.
     */
    public void setDefaultExpirationSeconds(int defaultExpirationSeconds) {
        this.defaultExpirationSeconds = defaultExpirationSeconds;
    }
}