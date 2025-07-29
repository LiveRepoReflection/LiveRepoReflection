import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.concurrent.*;
import java.util.*;

public class RateLimiterTest {

    // Dummy interface for the configuration service
    public interface ConfigurationService {
        RateLimitConfiguration getConfiguration(String clientId);
    }

    // Dummy configuration object
    public static class RateLimitConfiguration {
        private final int limit;
        private final long timeWindowMillis;

        public RateLimitConfiguration(int limit, long timeWindowMillis) {
            this.limit = limit;
            this.timeWindowMillis = timeWindowMillis;
        }

        public int getLimit() {
            return limit;
        }

        public long getTimeWindowMillis() {
            return timeWindowMillis;
        }
    }

    // Dummy implementation of ConfigurationService for testing
    public static class DummyConfigurationService implements ConfigurationService {
        private final Map<String, RateLimitConfiguration> configMap = new HashMap<>();

        public DummyConfigurationService() {
            // For client1, allow 5 requests per 2000ms window.
            configMap.put("client1", new RateLimitConfiguration(5, 2000));
            // For client3, allow 10 requests per 1000ms window.
            configMap.put("client3", new RateLimitConfiguration(10, 1000));
        }

        @Override
        public RateLimitConfiguration getConfiguration(String clientId) {
            return configMap.get(clientId);
        }
    }

    // Simple thread-safe RateLimiter implementation for testing purposes.
    // In the actual solution, the RateLimiter would use a distributed data store,
    // but here we simulate the token bucket mechanism locally.
    public static class RateLimiter {
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

    private RateLimiter rateLimiter;
    private DummyConfigurationService configurationService;

    @BeforeEach
    public void setUp() {
        configurationService = new DummyConfigurationService();
        rateLimiter = new RateLimiter(configurationService);
    }

    @Test
    public void testAllowWithinLimit() {
        String clientId = "client1";
        // Allow up to 5 requests within the time window.
        for (int i = 0; i < 5; i++) {
            boolean allowed = rateLimiter.allowRequest(clientId);
            assertTrue(allowed, "Request " + (i + 1) + " should be allowed");
        }
        // The 6th request should be rejected.
        boolean allowed = rateLimiter.allowRequest(clientId);
        assertFalse(allowed, "6th request should be rejected after limit is reached");
    }

    @Test
    public void testTimeWindowReset() throws InterruptedException {
        String clientId = "client1";
        // Use all tokens.
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(clientId));
        }
        assertFalse(rateLimiter.allowRequest(clientId), "Request should be rejected after limit is reached");
        // Wait for the time window to expire (window is 2000ms).
        Thread.sleep(2100);
        // New requests should now be allowed.
        boolean allowed = rateLimiter.allowRequest(clientId);
        assertTrue(allowed, "Request should be allowed after time window reset");
    }

    @Test
    public void testNonExistentClient() {
        String clientId = "non_existent";
        // Without configuration, the request should be rejected.
        boolean allowed = rateLimiter.allowRequest(clientId);
        assertFalse(allowed, "Request should be rejected for a client with no configuration");
    }

    @Test
    public void testConcurrentRequests() throws InterruptedException, ExecutionException {
        String clientId = "client3"; // Limit is 10 per 1000ms
        int numThreads = 20;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        for (int i = 0; i < numThreads; i++) {
            tasks.add(() -> rateLimiter.allowRequest(clientId));
        }

        List<Future<Boolean>> results = executor.invokeAll(tasks);
        executor.shutdown();
        int successCount = 0;
        for (Future<Boolean> future : results) {
            if (future.get()) {
                successCount++;
            }
        }
        // Only 10 requests should be allowed concurrently.
        assertEquals(10, successCount, "Only 10 requests should be allowed concurrently for client3");
    }
}