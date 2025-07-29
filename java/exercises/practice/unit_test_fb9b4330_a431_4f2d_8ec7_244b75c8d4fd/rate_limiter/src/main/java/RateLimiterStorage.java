public interface RateLimiterStorage {
    /**
     * Increment the request count for a given client and check if it's allowed
     * @param clientId The identifier of the client making the request
     * @param maxRequests The maximum number of requests allowed in the time window
     * @param timeWindowInSeconds The time window in seconds
     * @return true if the request is allowed, false otherwise
     * @throws DistributedRateLimiterException if there's an error with the storage
     */
    boolean incrementAndCheckLimit(String clientId, int maxRequests, int timeWindowInSeconds) 
            throws DistributedRateLimiterException;
    
    /**
     * Clean up any resources held by the storage implementation
     */
    void close();
}