import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class DistributedLimiterTest {

    private DistributedRateLimiter rateLimiter;

    @BeforeEach
    public void setUp() {
        // Instantiate the DistributedRateLimiter.
        // It is assumed that DistributedRateLimiter has a default constructor.
        rateLimiter = new DistributedRateLimiter();
    }

    @Test
    public void testSingleThreadWithinLimit() {
        String resource = "api_endpoint";
        String client = "client1";
        // Configure the rate limiter: allow 5 requests per 1000 milliseconds.
        rateLimiter.setRateLimit(resource, 5, 1000);

        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.isAllowed(resource, client), "Request " + (i + 1) + " should be allowed");
        }
    }

    @Test
    public void testSingleThreadExceedLimit() {
        String resource = "api_endpoint";
        String client = "client1";
        // Configure the rate limiter: allow 3 requests per 1000 milliseconds.
        rateLimiter.setRateLimit(resource, 3, 1000);

        for (int i = 0; i < 3; i++) {
            assertTrue(rateLimiter.isAllowed(resource, client), "Request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.isAllowed(resource, client), "Fourth request should be denied");
    }

    @Test
    public void testWindowReset() throws InterruptedException {
        String resource = "api_endpoint";
        String client = "client1";
        // Configure the rate limiter: allow 2 requests per 200 milliseconds.
        rateLimiter.setRateLimit(resource, 2, 200);

        // Make 2 requests; both should be allowed.
        assertTrue(rateLimiter.isAllowed(resource, client));
        assertTrue(rateLimiter.isAllowed(resource, client));
        // The third request in the same time window should be denied.
        assertFalse(rateLimiter.isAllowed(resource, client));

        // Wait for the window to expire.
        Thread.sleep(250);

        // After the window reset, 2 new requests should be allowed.
        assertTrue(rateLimiter.isAllowed(resource, client));
        assertTrue(rateLimiter.isAllowed(resource, client));
        // The next request should be denied again.
        assertFalse(rateLimiter.isAllowed(resource, client));
    }

    @Test
    public void testConcurrentRequests() throws InterruptedException, ExecutionException {
        String resource = "api_endpoint";
        String client = "client1";
        final int limit = 100;
        final int threadCount = 10;
        final int iterationsPerThread = 20; // Total 200 requests attempted concurrently.
        // Configure the rate limiter: allow 'limit' requests per 1000 milliseconds.
        rateLimiter.setRateLimit(resource, limit, 1000);

        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        AtomicInteger allowedCount = new AtomicInteger(0);

        Callable<Void> task = () -> {
            startLatch.await();
            for (int i = 0; i < iterationsPerThread; i++) {
                if (rateLimiter.isAllowed(resource, client)) {
                    allowedCount.incrementAndGet();
                }
            }
            return null;
        };

        Future<Void>[] futures = new Future[threadCount];
        for (int i = 0; i < threadCount; i++) {
            futures[i] = executor.submit(task);
        }
        startLatch.countDown();

        for (Future<Void> future : futures) {
            future.get();
        }
        executor.shutdown();

        // The total number of allowed requests should equal the specified limit.
        assertEquals(limit, allowedCount.get(), "Total allowed requests should equal the rate limit");
    }
}