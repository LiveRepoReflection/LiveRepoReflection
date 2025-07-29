import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedRateLimiterTest {

    @Test
    public void testSingleClientWithinLimit() throws Exception {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String clientId = "client1";
        // Set rate limit for client1 to 5 requests per second
        limiter.setRateLimit(clientId, 5);

        // Allow 5 requests in the same time window
        for (int i = 0; i < 5; i++) {
            boolean allowed = limiter.shouldAllow(clientId);
            assertTrue(allowed, "Request " + (i + 1) + " should be allowed");
        }

        // The 6th request in the same time window should be rejected
        assertFalse(limiter.shouldAllow(clientId), "6th request should be rejected");

        // Wait for new time window (a bit more than 1 second)
        Thread.sleep(1100);
        assertTrue(limiter.shouldAllow(clientId), "After new time window, request should be allowed");
    }

    @Test
    public void testMultipleClientsIndependentLimits() throws Exception {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String clientA = "clientA";
        String clientB = "clientB";
        limiter.setRateLimit(clientA, 3);
        limiter.setRateLimit(clientB, 2);

        // Test clientA: 3 allowed, then rejection
        for (int i = 0; i < 3; i++) {
            assertTrue(limiter.shouldAllow(clientA), "ClientA request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientA), "ClientA 4th request should be rejected");

        // Test clientB: 2 allowed, then rejection
        for (int i = 0; i < 2; i++) {
            assertTrue(limiter.shouldAllow(clientB), "ClientB request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientB), "ClientB 3rd request should be rejected");
    }

    @Test
    public void testRateLimitResetAfterWindow() throws Exception {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String clientId = "clientReset";
        limiter.setRateLimit(clientId, 2);

        // Exhaust limit in the current time window
        for (int i = 0; i < 2; i++) {
            assertTrue(limiter.shouldAllow(clientId), "Request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientId), "Exceeding the limit should be rejected");

        // Wait for the time window to expire (a little over a second)
        Thread.sleep(1100);

        // After reset, requests should be allowed again
        for (int i = 0; i < 2; i++) {
            assertTrue(limiter.shouldAllow(clientId), "After reset, request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientId), "Exceeding the new window should be rejected again");
    }

    @Test
    public void testDynamicRateLimitUpdate() throws Exception {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String clientId = "dynamicClient";
        limiter.setRateLimit(clientId, 2);

        // Initially, allow 2 requests
        for (int i = 0; i < 2; i++) {
            assertTrue(limiter.shouldAllow(clientId), "Initial request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientId), "Initial extra request should be rejected");

        // Dynamically update the rate limit to 4 for the client
        limiter.setRateLimit(clientId, 4);
        Thread.sleep(1100);

        for (int i = 0; i < 4; i++) {
            assertTrue(limiter.shouldAllow(clientId), "After update, request " + (i + 1) + " should be allowed");
        }
        assertFalse(limiter.shouldAllow(clientId), "After update, extra request should be rejected");
    }

    @Test
    public void testConcurrency() throws Exception {
        final DistributedRateLimiter limiter = new DistributedRateLimiter();
        final String clientId = "concurrentClient";
        // Set a high rate limit to test concurrency
        limiter.setRateLimit(clientId, 1000);

        ExecutorService executor = Executors.newFixedThreadPool(10);
        final AtomicInteger allowedCount = new AtomicInteger(0);
        final int totalRequests = 1000;
        CountDownLatch latch = new CountDownLatch(totalRequests);

        // Submit concurrent requests
        for (int i = 0; i < totalRequests; i++) {
            executor.submit(() -> {
                if (limiter.shouldAllow(clientId)) {
                    allowedCount.incrementAndGet();
                }
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();

        // The number of allowed requests should match the rate limit
        assertEquals(1000, allowedCount.get(), "Allowed count should equal the set rate limit");
    }

    @Test
    public void testExceedingRateInConcurrentEnvironment() throws Exception {
        final DistributedRateLimiter limiter = new DistributedRateLimiter();
        final String clientId = "highConcurrencyClient";
        limiter.setRateLimit(clientId, 500);

        ExecutorService executor = Executors.newFixedThreadPool(20);
        final AtomicInteger successCount = new AtomicInteger(0);
        final int totalRequests = 1000;
        CountDownLatch latch = new CountDownLatch(totalRequests);

        // Concurrently submit requests that exceed the limit
        for (int i = 0; i < totalRequests; i++) {
            executor.submit(() -> {
                if (limiter.shouldAllow(clientId)) {
                    successCount.incrementAndGet();
                }
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();

        // The allowed requests must not exceed the rate limit
        assertEquals(500, successCount.get(), "Should allow exactly 500 requests in the current window");
    }
}