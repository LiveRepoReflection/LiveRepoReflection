public interface DistributedRateLimiter {
    /**
     * Check if a request from the client is allowed based on configured rate limits
     * @param clientId The identifier of the client making the request
     * @param maxRequests The maximum number of requests allowed in the time window
     * @param timeWindowInSeconds The time window in seconds
     * @return true if the request is allowed, false otherwise
     */
    boolean isAllowed(String clientId, int maxRequests, int timeWindowInSeconds);
    
    /**
     * Clean up any resources held by the rate limiter
     */
    void close();
}