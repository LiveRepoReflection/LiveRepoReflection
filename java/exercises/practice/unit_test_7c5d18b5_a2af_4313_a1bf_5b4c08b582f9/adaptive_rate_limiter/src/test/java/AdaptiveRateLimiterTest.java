import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class AdaptiveRateLimiterTest {

    /**
     * This test verifies that a single request is allowed when within the default rate limit.
     */
    @Test
    void testAllowSingleRequestWithinRateLimit() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        boolean allowed = limiter.allowRequest("endpoint1", "client1");
        assertTrue(allowed, "The first request should be allowed.");
    }

    /**
     * This test verifies that requests exceeding the client-specific rate limit are rejected.
     */
    @Test
    void testRateLimitingForClient() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        // Simulate a scenario with a preset client-specific limit. Assume the limit is 5 requests.
        for (int i = 0; i < 5; i++) {
            assertTrue(limiter.allowRequest("endpoint1", "client1"),
                       "Request " + (i + 1) + " should be allowed for client1.");
        }
        // The 6th request should be rejected.
        assertFalse(limiter.allowRequest("endpoint1", "client1"),
                    "The 6th request should be rejected due to rate limiting.");
    }

    /**
     * This test verifies that different API endpoints maintain their own rate limits.
     */
    @Test
    void testDifferentEndpointsSeparateRateLimits() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        // Assume each endpoint has a separate limit of 5 requests per client.
        for (int i = 0; i < 5; i++) {
            assertTrue(limiter.allowRequest("/users", "clientA"),
                       "Request " + (i + 1) + " for /users should be allowed.");
            assertTrue(limiter.allowRequest("/products", "clientA"),
                       "Request " + (i + 1) + " for /products should be allowed.");
        }
        // Further requests for each endpoint should be rejected.
        assertFalse(limiter.allowRequest("/users", "clientA"),
                    "6th request for /users should be rejected.");
        assertFalse(limiter.allowRequest("/products", "clientA"),
                    "6th request for /products should be rejected.");
    }

    /**
     * This test simulates backend overload and verifies that the adaptive throttling mechanism
     * reduces the allowed number of requests.
     */
    @Test
    void testAdaptiveThrottleBehaviorUnderBackendOverload() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        // Simulate backend overload by updating backend status with high response time and error rate.
        limiter.updateBackendStatus(1000, 0.5);
        
        int allowedCount = 0;
        // Attempt 10 requests on an endpoint which should be throttled aggressively.
        for (int i = 0; i < 10; i++) {
            if (limiter.allowRequest("/overloaded", "clientB")) {
                allowedCount++;
            }
        }
        // Assuming that adaptive throttling reduces the allowable requests to at most 3.
        assertTrue(allowedCount <= 3, "Allowed requests during overload should be 3 or fewer.");
    }

    /**
     * This test verifies that the limiter recovers from backend overload by gradually increasing
     * the allowed request rate once backend performance improves.
     */
    @Test
    void testRecoveryFromBackendOverload() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        // First simulate overload.
        limiter.updateBackendStatus(1000, 0.5);
        for (int i = 0; i < 10; i++) {
            limiter.allowRequest("/recover", "clientC");
        }
        int allowedDuringOverload = 0;
        for (int i = 0; i < 10; i++) {
            if (limiter.allowRequest("/recover", "clientC")) {
                allowedDuringOverload++;
            }
        }
        // Now simulate recovery with lower response time and error rate.
        limiter.updateBackendStatus(100, 0.0);
        int allowedAfterRecovery = 0;
        for (int i = 0; i < 10; i++) {
            if (limiter.allowRequest("/recover", "clientC")) {
                allowedAfterRecovery++;
            }
        }
        // After recovery, the allowance should be higher than during the overload.
        assertTrue(allowedAfterRecovery > allowedDuringOverload,
                   "Allowed requests after recovery should exceed those during overload.");
    }

    /**
     * This test verifies that a global rate limit is enforced across multiple clients for a single endpoint.
     */
    @Test
    void testGlobalRateLimit() {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        // Assume a global rate limit of 10 requests for the endpoint "/global".
        int globalLimit = 10;
        int allowedCount = 0;
        for (int i = 0; i < 20; i++) {
            String clientId = "client" + (i % 3);
            if (limiter.allowRequest("/global", clientId)) {
                allowedCount++;
            }
        }
        assertTrue(allowedCount <= globalLimit,
                   "Total allowed requests for /global should not exceed the global rate limit.");
    }

    /**
     * This test verifies that concurrent requests are handled properly and the rate limiter
     * maintains thread safety.
     */
    @Test
    void testConcurrentRequests() throws Exception {
        AdaptiveRateLimiter limiter = new AdaptiveRateLimiter();
        int threads = 20;
        int requestsPerThread = 10;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        List<Callable<Integer>> tasks = new ArrayList<>();

        // Each thread simulates a different client sending requests.
        for (int i = 0; i < threads; i++) {
            final String clientId = "client" + i;
            tasks.add(() -> {
                int allowed = 0;
                for (int j = 0; j < requestsPerThread; j++) {
                    if (limiter.allowRequest("/concurrent", clientId)) {
                        allowed++;
                    }
                }
                return allowed;
            });
        }

        List<Future<Integer>> results = executor.invokeAll(tasks);
        int totalAllowed = 0;
        for (Future<Integer> future : results) {
            totalAllowed += future.get();
        }
        executor.shutdown();
        // For testing purposes, assume that the global limit for "/concurrent" is 15.
        assertTrue(totalAllowed <= 15,
                   "Total allowed concurrent requests should not exceed the global limit.");
    }
}