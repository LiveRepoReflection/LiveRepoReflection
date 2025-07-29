import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;

public class RateLimiter {

    private final ConcurrentHashMap<Key, RateLimiterBucket> bucketMap = new ConcurrentHashMap<>();

    /**
     * Configure rate limit settings for a specific client and endpoint.
     *
     * @param clientId    Unique identifier for the client.
     * @param endpoint    API endpoint for which the rate limit applies.
     * @param maxRequests Maximum number of requests allowed in the given time window.
     * @param windowMillis Duration of the time window in milliseconds.
     */
    public void configure(String clientId, String endpoint, int maxRequests, long windowMillis) {
        Key key = new Key(clientId, endpoint);
        // When reconfiguring, the new configuration will reset the bucket.
        RateLimiterBucket newBucket = new RateLimiterBucket(maxRequests, windowMillis);
        bucketMap.put(key, newBucket);
    }

    /**
     * Allow a request if the rate limit has not been exceeded.
     *
     * @param clientId Unique identifier for the client.
     * @param endpoint API endpoint being accessed.
     * @return true if the request is allowed, false otherwise.
     */
    public boolean allow(String clientId, String endpoint) {
        Key key = new Key(clientId, endpoint);
        RateLimiterBucket bucket = bucketMap.get(key);
        if (bucket == null) {
            // If no configuration is present for the key, deny the request.
            return false;
        }
        return bucket.allowRequest();
    }

    /**
     * Composite key class combining clientId and endpoint.
     */
    private static class Key {
        private final String clientId;
        private final String endpoint;

        public Key(String clientId, String endpoint) {
            this.clientId = clientId;
            this.endpoint = endpoint;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof Key)) return false;
            Key key = (Key) o;
            return Objects.equals(clientId, key.clientId) && Objects.equals(endpoint, key.endpoint);
        }

        @Override
        public int hashCode() {
            return Objects.hash(clientId, endpoint);
        }
    }

    /**
     * Bucket class to track request counts and window timings.
     */
    private static class RateLimiterBucket {
        private final int maxRequests;
        private final long windowMillis;
        private long windowStart;
        private int requestCount;

        public RateLimiterBucket(int maxRequests, long windowMillis) {
            this.maxRequests = maxRequests;
            this.windowMillis = windowMillis;
            this.windowStart = System.currentTimeMillis();
            this.requestCount = 0;
        }

        /**
         * Evaluates the current request and decides if it should be allowed based on fixed window rate limiting.
         *
         * @return true if the request is allowed, false if the rate limit is exceeded.
         */
        public synchronized boolean allowRequest() {
            long currentTime = System.currentTimeMillis();
            if (currentTime - windowStart >= windowMillis) {
                // Reset the window.
                windowStart = currentTime;
                requestCount = 0;
            }
            if (requestCount < maxRequests) {
                requestCount++;
                return true;
            }
            return false;
        }
    }
}