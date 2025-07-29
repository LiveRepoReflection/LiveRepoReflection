import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

public class RateLimiterTest {

    private RateLimiter rateLimiter;

    @BeforeEach
    public void setup() {
        // Initialize the RateLimiter instance.
        // It is assumed that RateLimiter has a default constructor and supports dynamic configuration.
        rateLimiter = new RateLimiter();
    }

    @Test
    public void testBasicRateLimit() {
        String clientId = "client1";
        String endpoint = "/api/search";
        // Configure rate limit: 5 requests per 1000 milliseconds.
        rateLimiter.configure(clientId, endpoint, 5, 1000);

        // Issue 5 requests which should be allowed.
        for (int i = 0; i < 5; i++) {
            assertTrue(rateLimiter.allow(clientId, endpoint), "Request " + (i + 1) + " should be allowed");
        }
        // The 6th request should be rejected.
        assertFalse(rateLimiter.allow(clientId, endpoint), "6th request should be rejected");
    }

    @Test
    public void testWindowExpiration() throws InterruptedException {
        String clientId = "client2";
        String endpoint = "/api/order";
        // Configure rate limit: 3 requests per 500 milliseconds.
        rateLimiter.configure(clientId, endpoint, 3, 500);

        // Issue 3 requests which should be allowed.
        for (int i = 0; i < 3; i++) {
            assertTrue(rateLimiter.allow(clientId, endpoint), "Request " + (i + 1) + " should be allowed");
        }
        // The 4th request is expected to be rejected.
        assertFalse(rateLimiter.allow(clientId, endpoint), "4th request should be rejected");

        // Wait for the time window to expire.
        Thread.sleep(600);

        // After window expiration, the request counter resets.
        assertTrue(rateLimiter.allow(clientId, endpoint), "Request should be allowed after window reset");
    }

    @Test
    public void testMultipleClientsAndEndpoints() {
        String clientA = "clientA";
        String clientB = "clientB";
        String endpointX = "/api/search";
        String endpointY = "/api/cart";

        // Configure rate limits for different client-endpoint pairs.
        rateLimiter.configure(clientA, endpointX, 4, 1000);
        rateLimiter.configure(clientA, endpointY, 2, 1000);
        rateLimiter.configure(clientB, endpointX, 3, 1000);

        // For clientA, endpointX: 4 allowed and 5th rejected.
        for (int i = 0; i < 4; i++) {
            assertTrue(rateLimiter.allow(clientA, endpointX), "ClientA endpointX request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.allow(clientA, endpointX), "ClientA endpointX 5th request should be rejected");

        // For clientA, endpointY: 2 allowed and 3rd rejected.
        for (int i = 0; i < 2; i++) {
            assertTrue(rateLimiter.allow(clientA, endpointY), "ClientA endpointY request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.allow(clientA, endpointY), "ClientA endpointY 3rd request should be rejected");

        // For clientB, endpointX: 3 allowed and 4th rejected.
        for (int i = 0; i < 3; i++) {
            assertTrue(rateLimiter.allow(clientB, endpointX), "ClientB endpointX request " + (i + 1) + " should be allowed");
        }
        assertFalse(rateLimiter.allow(clientB, endpointX), "ClientB endpointX 4th request should be rejected");
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testConcurrency() throws InterruptedException {
        String clientId = "client_concurrent";
        String endpoint = "/api/burst";
        final int maxRequests = 50;
        final int windowMillis = 1000;
        rateLimiter.configure(clientId, endpoint, maxRequests, windowMillis);

        final int threadCount = 10;
        final int requestsPerThread = 10; // Total of 100 requests, but only 50 should be allowed.
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);
        final int[] allowedCount = {0};

        for (int i = 0; i < threadCount; i++) {
            executor.submit(() -> {
                for (int j = 0; j < requestsPerThread; j++) {
                    if (rateLimiter.allow(clientId, endpoint)) {
                        synchronized (allowedCount) {
                            allowedCount[0]++;
                        }
                    }
                }
                latch.countDown();
            });
        }

        latch.await();
        executor.shutdown();
        // Only maxRequests should be allowed.
        assertEquals(maxRequests, allowedCount[0], "Total allowed requests should equal the configured maximum");
    }

    @Test
    public void testDynamicConfiguration() throws InterruptedException {
        String clientId = "client_dynamic";
        String endpoint = "/api/update";
        // Initial configuration: 2 requests per 1000 milliseconds.
        rateLimiter.configure(clientId, endpoint, 2, 1000);

        // Execute 2 requests which should be allowed.
        assertTrue(rateLimiter.allow(clientId, endpoint), "First request should be allowed");
        assertTrue(rateLimiter.allow(clientId, endpoint), "Second request should be allowed");
        // The 3rd request is expected to be rejected.
        assertFalse(rateLimiter.allow(clientId, endpoint), "3rd request should be rejected under initial configuration");

        // Dynamically update the configuration to allow 4 requests per 1000 milliseconds.
        rateLimiter.configure(clientId, endpoint, 4, 1000);

        // Wait for the previous time window to expire.
        Thread.sleep(1100);

        // Now 4 consecutive requests should be allowed.
        for (int i = 0; i < 4; i++) {
            assertTrue(rateLimiter.allow(clientId, endpoint), "Request " + (i + 1) + " should be allowed after dynamic reconfiguration");
        }
        // A 5th request should be rejected.
        assertFalse(rateLimiter.allow(clientId, endpoint), "5th request should be rejected under new configuration");
    }
}