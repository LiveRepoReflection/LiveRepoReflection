public class DefaultDistributedRateLimiter implements DistributedRateLimiter {
    private final RateLimiterStorage storage;
    
    public DefaultDistributedRateLimiter(RateLimiterStorage storage) {
        this.storage = storage;
    }
    
    @Override
    public boolean isAllowed(String clientId, int maxRequests, int timeWindowInSeconds) {
        try {
            return storage.incrementAndCheckLimit(clientId, maxRequests, timeWindowInSeconds);
        } catch (DistributedRateLimiterException e) {
            // In case of storage errors, we'll allow the request to proceed
            // This is a fail-open approach, but can be configured differently based on requirements
            return true;
        }
    }
    
    @Override
    public void close() {
        storage.close();
    }
}