import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.concurrent.*;
import java.util.*;

class DistributedLimiterTest {

    private DistributedLimiter limiterGlobal;
    private DistributedLimiter limiterServer;
    private DistributedLimiter limiterHybrid;

    @BeforeEach
    void setup() {
        // Assuming DistributedLimiter has a constructor with signature:
        // DistributedLimiter(int limit, int timeWindowSeconds, String granularity,
        //                    int tolerance, String evictionPolicy, int evictionDurationSeconds)
        // For GLOBAL and SERVER modes, tolerance is ignored.
        limiterGlobal = new DistributedLimiter(5, 10, "GLOBAL", 0, "TTL", 15);
        limiterServer = new DistributedLimiter(5, 10, "SERVER", 0, "LRU", 15);
        limiterHybrid = new DistributedLimiter(5, 10, "HYBRID", 10, "TTL", 15);
    }

    @Test
    void testAllowRequestGlobal() {
        String apiKey = "user_global";
        // Allow first 5 requests
        for (int i = 0; i < 5; i++) {
            assertTrue(limiterGlobal.allowRequest(apiKey), "Request " + (i + 1) + " should be allowed in GLOBAL mode");
        }
        // 6th request should not be allowed because limit is reached
        assertFalse(limiterGlobal.allowRequest(apiKey), "6th request should be blocked for GLOBAL mode");
    }

    @Test
    void testAllowRequestServer() {
        String apiKey = "user_server";
        // In SERVER mode, each instance maintains its own counter.
        // Simulate two separate server instances.
        DistributedLimiter anotherServerLimiter = new DistributedLimiter(5, 10, "SERVER", 0, "LRU", 15);

        // On first server, allow 5 requests
        for (int i = 0; i < 5; i++) {
            assertTrue(limiterServer.allowRequest(apiKey), "Request " + (i + 1) + " should be allowed on server1");
        }
        // 6th request on first server should be blocked.
        assertFalse(limiterServer.allowRequest(apiKey), "6th request should be blocked on server1");

        // On second server, counter is independent, so allow 5 requests
        for (int i = 0; i < 5; i++) {
            assertTrue(anotherServerLimiter.allowRequest(apiKey), "Request " + (i + 1) + " should be allowed on server2");
        }
        assertFalse(anotherServerLimiter.allowRequest(apiKey), "6th request should be blocked on server2");
    }

    @Test
    void testAllowRequestHybrid() {
        String apiKey = "user_hybrid";
        // In HYBRID mode with a tolerance of 10%, extra allowed requests are calculated as:
        // extra = floor(limit * tolerance/100). For limit = 5 and 10% tolerance, extra = floor(0.5) = 0.
        // Thus, normally only 5 requests are allowed. However, the tolerance mechanism could allow a transient overshoot.
        int expectedAllowed = 5;  // minimum allowed
        for (int i = 0; i < expectedAllowed; i++) {
            assertTrue(limiterHybrid.allowRequest(apiKey), "Request " + (i + 1) + " should be allowed in HYBRID mode");
        }
        // Next request should be blocked even with tolerance considered.
        assertFalse(limiterHybrid.allowRequest(apiKey), "Request exceeding tolerance should be blocked in HYBRID mode");
    }

    @Test
    void testConcurrentAccessGlobal() throws InterruptedException, ExecutionException {
        String apiKey = "user_concurrent";
        int threadCount = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();
        // In GLOBAL mode, only 5 requests are allowed concurrently within the time window.
        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> limiterGlobal.allowRequest(apiKey));
        }
        List<Future<Boolean>> results = executor.invokeAll(tasks);
        int allowedCount = 0;
        for (Future<Boolean> future : results) {
            if (future.get()) {
                allowedCount++;
            }
        }
        // Verify exactly 5 concurrent requests are allowed.
        assertEquals(5, allowedCount, "Exactly 5 concurrent requests should be allowed in GLOBAL mode");
        executor.shutdown();
    }

    @Test
    void testEvictionPolicyTTL() throws InterruptedException {
        String apiKey = "user_eviction";
        // Send a few requests initially.
        for (int i = 0; i < 3; i++) {
            assertTrue(limiterGlobal.allowRequest(apiKey), "Initial request " + (i + 1) + " should be allowed");
        }
        // Wait for longer than the eviction duration (15 seconds) to simulate counter eviction.
        Thread.sleep(16000);
        // After eviction, counters should reset allowing full usage.
        for (int i = 0; i < 5; i++) {
            assertTrue(limiterGlobal.allowRequest(apiKey), "Post-eviction, request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiterGlobal.allowRequest(apiKey), "Post-eviction, exceeding limit should block request");
    }

    @Test
    void testRateLimiterResetBetweenWindows() throws InterruptedException {
        String apiKey = "user_reset";
        // Exhaust requests in current window.
        for (int i = 0; i < 5; i++) {
            assertTrue(limiterGlobal.allowRequest(apiKey), "Request " + (i + 1) + " should be allowed in current window");
        }
        assertFalse(limiterGlobal.allowRequest(apiKey), "Should block when limit is reached in current window");
        // Wait until the time window expires (10 seconds) and a little extra.
        Thread.sleep(11000);
        // New window: requests should be allowed again.
        for (int i = 0; i < 5; i++) {
            assertTrue(limiterGlobal.allowRequest(apiKey), "After window reset, request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiterGlobal.allowRequest(apiKey), "After window reset, exceeding limit should block request");
    }

    @Test
    void testMultipleApiKeys() {
        String[] apiKeys = {"user1", "user2", "user3", "user4", "user5"};
        // Each API key should be independently rate limited.
        for (String key : apiKeys) {
            for (int i = 0; i < 5; i++) {
                assertTrue(limiterGlobal.allowRequest(key), "Request " + (i + 1) + " should be allowed for API key: " + key);
            }
            assertFalse(limiterGlobal.allowRequest(key), "6th request for API key " + key + " should be blocked");
        }
    }
}