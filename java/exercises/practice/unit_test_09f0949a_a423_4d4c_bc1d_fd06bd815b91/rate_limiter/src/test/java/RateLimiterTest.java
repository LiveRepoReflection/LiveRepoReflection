package rate_limiter;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class RateLimiterTest {

    private RateLimiter rateLimiter;

    @Before
    public void setup() {
        // Assuming RateLimiterImpl is the implemented class of the RateLimiter interface.
        // The constructor takes two parameters: maxRequests and timeWindowInMillis.
        rateLimiter = new RateLimiterImpl(5, 1000);
    }

    @Test
    public void testAllowUpToLimit() {
        String clientId = "client1";
        // Allow up to 5 requests in a time window.
        for (int i = 0; i < 5; i++) {
            Assert.assertTrue("Request " + (i + 1) + " should be allowed", rateLimiter.allowRequest(clientId));
        }
        // The 6th request should be blocked.
        Assert.assertFalse("Request 6 should be blocked", rateLimiter.allowRequest(clientId));
    }

    @Test
    public void testResetAfterTimeWindow() throws InterruptedException {
        String clientId = "client2";
        // Consume the allowed requests.
        for (int i = 0; i < 5; i++) {
            Assert.assertTrue(rateLimiter.allowRequest(clientId));
        }
        Assert.assertFalse(rateLimiter.allowRequest(clientId));
        // Wait for the time window to expire.
        Thread.sleep(1100);
        // After the time window resets, the client should be allowed to make requests again.
        for (int i = 0; i < 5; i++) {
            Assert.assertTrue(rateLimiter.allowRequest(clientId));
        }
        Assert.assertFalse(rateLimiter.allowRequest(clientId));
    }

    @Test
    public void testConcurrentRequests() throws InterruptedException {
        // Test concurrent access by simulating multiple threads issuing requests for the same client.
        final String clientId = "client3";
        final int totalThreads = 20;
        ExecutorService executor = Executors.newFixedThreadPool(totalThreads);
        final CountDownLatch latch = new CountDownLatch(totalThreads);
        final int[] allowedCount = {0};

        for (int i = 0; i < totalThreads; i++) {
            executor.submit(() -> {
                if (rateLimiter.allowRequest(clientId)) {
                    synchronized (allowedCount) {
                        allowedCount[0]++;
                    }
                }
                latch.countDown();
            });
        }
        latch.await();
        // Only 5 requests should be allowed in the given time window.
        Assert.assertEquals("Concurrent requests allowed should be 5", 5, allowedCount[0]);
        executor.shutdown();
    }

    @Test
    public void testMultipleClients() {
        // Ensure that rate limiting is maintained per client independently.
        String clientA = "clientA";
        String clientB = "clientB";
        for (int i = 0; i < 5; i++) {
            Assert.assertTrue(rateLimiter.allowRequest(clientA));
            Assert.assertTrue(rateLimiter.allowRequest(clientB));
        }
        // Both clients should be rate limited after their 5 requests.
        Assert.assertFalse(rateLimiter.allowRequest(clientA));
        Assert.assertFalse(rateLimiter.allowRequest(clientB));
    }
}