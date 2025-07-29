import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class RateLimiterTest {

    private RateLimiter rateLimiter;

    @BeforeEach
    public void setup() {
        // Initialize RateLimiter with a limit of 5 requests per 2 seconds
        // Assumes RateLimiter constructor: RateLimiter(int maxRequests, long windowMillis)
        rateLimiter = new RateLimiter(5, 2000);
    }

    @Test
    public void testUnderLimitSingleUser() {
        String user = "user1";
        // Send 5 requests which should be allowed
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(user), "Request " + (i + 1) + " should be allowed");
        }
    }

    @Test
    public void testExceedLimitSingleUser() {
        String user = "user1";
        // Send 5 allowed requests
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(user), "Request " + (i + 1) + " should be allowed");
        }
        // The 6th request should be rejected
        assertFalse(rateLimiter.allowRequest(user), "6th request should be rejected");
    }

    @Test
    public void testMultipleUsersIndependentLimits() {
        String userA = "userA";
        String userB = "userB";
        // Both users should be able to send up to 5 requests independently
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(userA), "UserA, request " + (i + 1) + " should be allowed");
            assertTrue(rateLimiter.allowRequest(userB), "UserB, request " + (i + 1) + " should be allowed");
        }
        // Both should be rejected on the 6th request
        assertFalse(rateLimiter.allowRequest(userA), "UserA: 6th request should be rejected");
        assertFalse(rateLimiter.allowRequest(userB), "UserB: 6th request should be rejected");
    }

    @Test
    public void testResetAfterWindowExpiration() throws InterruptedException {
        String user = "resetUser";
        // Use all allowed requests within the window
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(user), "Request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.allowRequest(user), "6th request should be rejected within the same window");
        
        // Wait for window to expire (slightly longer than 2 seconds)
        Thread.sleep(2100);
        
        // Now requests should be allowed again
        assertTrue(rateLimiter.allowRequest(user), "Request after window reset should be allowed");
    }

    @Test
    @Timeout(10)
    public void testConcurrentAccessSingleUser() throws InterruptedException, ExecutionException {
        String user = "concurrentUser";
        int threadCount = 10;
        int requestsPerThread = 5;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch startLatch = new CountDownLatch(1);
        AtomicInteger allowedCount = new AtomicInteger(0);
        Callable<Void> task = () -> {
            startLatch.await();
            for (int i = 0; i < requestsPerThread; i++) {
                if (rateLimiter.allowRequest(user)) {
                    allowedCount.incrementAndGet();
                }
            }
            return null;
        };

        Future<?>[] futures = new Future[threadCount];
        for (int i = 0; i < threadCount; i++) {
            futures[i] = executor.submit(task);
        }

        startLatch.countDown(); // start all threads
        for (int i = 0; i < threadCount; i++) {
            futures[i].get();
        }
        executor.shutdown();

        // In total, only 5 requests should have been allowed,
        // even when requests were made concurrently.
        assertEquals(5, allowedCount.get(), "Only 5 requests should be allowed concurrently for a single user");
    }

    @Test
    public void testDynamicConfigurationUpdate() throws InterruptedException {
        String user = "dynamicUser";
        // Initially, 5 requests allowed per 2 seconds
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allowRequest(user), "Initial allowed request " + (i + 1));
        }
        assertFalse(rateLimiter.allowRequest(user), "6th request should be rejected initially");

        // Simulate a dynamic update to the rate limit: increase to 10 requests per 2 seconds.
        // Assumes RateLimiter provides a method updateLimit(int newMaxRequests, long newWindowMillis)
        rateLimiter.updateLimit(10, 2000);

        // Wait for current window to expire
        Thread.sleep(2100);

        // After dynamic update, 10 requests should be allowed
        for (int i = 0; i < 10; i++) {
            assertTrue(rateLimiter.allowRequest(user), "After config update, request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.allowRequest(user), "11th request should be rejected after config update");
    }
}