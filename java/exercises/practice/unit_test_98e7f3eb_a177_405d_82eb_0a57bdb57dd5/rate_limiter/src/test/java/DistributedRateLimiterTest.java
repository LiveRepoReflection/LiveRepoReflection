import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedRateLimiterTest {

    // Helper method to simulate waiting until the next time window (if required).
    private void sleepFor(double seconds) {
        try {
            Thread.sleep((long) (seconds * 1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Test
    public void testAllowRequestWithinRateLimit() {
        // Setup: Allow 5 requests per 2 seconds
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String userId = "user1";
        String resourceId = "resourceA";
        int limit = 5;
        int timeWindow = 2; // seconds

        // Send 5 requests which should be allowed.
        for (int i = 0; i < 5; i++) {
            boolean allowed = limiter.allowRequest(userId, resourceId, limit, timeWindow);
            Assertions.assertTrue(allowed, "Request " + (i + 1) + " should be allowed.");
        }
        // The 6th request in the same time window should be denied.
        boolean allowed = limiter.allowRequest(userId, resourceId, limit, timeWindow);
        Assertions.assertFalse(allowed, "6th request should be denied.");
    }

    @Test
    public void testTimeWindowReset() {
        // Setup: Allow 3 requests per 1 second
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String userId = "user2";
        String resourceId = "resourceB";
        int limit = 3;
        int timeWindow = 1; // seconds

        // Consume 3 requests.
        for (int i = 0; i < 3; i++) {
            boolean allowed = limiter.allowRequest(userId, resourceId, limit, timeWindow);
            Assertions.assertTrue(allowed, "Request " + (i + 1) + " should be allowed.");
        }
        // Next request should be denied.
        Assertions.assertFalse(limiter.allowRequest(userId, resourceId, limit, timeWindow), "Request should be denied after limit reached.");

        // Wait for time window to pass.
        sleepFor(1.1);
        // Now request should be allowed again.
        Assertions.assertTrue(limiter.allowRequest(userId, resourceId, limit, timeWindow), "Request should be allowed after time window reset.");
    }

    @Test
    public void testMultipleUsersAndResources() {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        int limit = 4;
        int timeWindow = 2; // seconds

        String[] users = {"userA", "userB", "userC"};
        String[] resources = {"resource1", "resource2"};

        // For each user-resource combination, perform limit tests.
        for (String user : users) {
            for (String resource : resources) {
                // Allow exactly 'limit' requests.
                for (int i = 0; i < limit; i++) {
                    boolean allowed = limiter.allowRequest(user, resource, limit, timeWindow);
                    Assertions.assertTrue(allowed, "User " + user + " accessing " + resource + " should allow request " + (i + 1));
                }
                // Additional request should be denied.
                boolean allowed = limiter.allowRequest(user, resource, limit, timeWindow);
                Assertions.assertFalse(allowed, "User " + user + " accessing " + resource + " should deny request beyond limit");
            }
        }
    }

    @Test
    public void testInvalidInputs() {
        DistributedRateLimiter limiter = new DistributedRateLimiter();
        String userId = "user_invalid";
        String resourceId = "resource_invalid";

        // Negative limit should probably throw an exception or result in a default behavior.
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            limiter.allowRequest(userId, resourceId, -1, 2);
        }, "Negative limit should trigger exception.");

        // Negative timeWindow should throw exception.
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            limiter.allowRequest(userId, resourceId, 5, -2);
        }, "Negative timeWindow should trigger exception.");

        // Zero limit is not valid.
        Assertions.assertThrows(IllegalArgumentException.class, () -> {
            limiter.allowRequest(userId, resourceId, 0, 2);
        }, "Zero limit should trigger exception.");
    }

    @Test
    public void testConcurrentRequests() throws InterruptedException {
        final DistributedRateLimiter limiter = new DistributedRateLimiter();
        final String userId = "concurrentUser";
        final String resourceId = "concurrentResource";
        final int limit = 100;
        final int timeWindow = 2; // seconds

        int threadCount = 10;
        int requestsPerThread = 20; // total 200 requests attempted concurrently
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch doneLatch = new CountDownLatch(threadCount);
        AtomicInteger allowedCount = new AtomicInteger(0);
        List<Thread> threads = new ArrayList<>();

        for (int i = 0; i < threadCount; i++) {
            Thread t = new Thread(() -> {
                try {
                    startLatch.await();
                    for (int j = 0; j < requestsPerThread; j++) {
                        if (limiter.allowRequest(userId, resourceId, limit, timeWindow)) {
                            allowedCount.incrementAndGet();
                        }
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    doneLatch.countDown();
                }
            });
            threads.add(t);
            t.start();
        }

        startLatch.countDown();
        doneLatch.await();

        // Only up to 'limit' number of requests should be allowed.
        int totalAllowed = allowedCount.get();
        Assertions.assertEquals(limit, totalAllowed, "Concurrent requests should not exceed the defined limit.");
    }
}