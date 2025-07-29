import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class RateLimiterTest {

    @Mock
    private TimeProvider timeProvider;

    private RateLimiter rateLimiter;

    @BeforeEach
    void setUp() {
        when(timeProvider.getCurrentTimeMillis()).thenReturn(Instant.now().toEpochMilli());
        rateLimiter = new RateLimiter(timeProvider);
    }

    @Test
    void shouldAllowFirstRequest() {
        boolean allowed = rateLimiter.isAllowed("user1", "api1");
        assertThat(allowed).isTrue();
    }

    @Test
    void shouldRespectRateLimit() {
        String userId = "user1";
        String apiId = "api1";
        
        // Simulate 100 requests
        IntStream.range(0, 100).forEach(i -> rateLimiter.isAllowed(userId, apiId));
        
        boolean allowed = rateLimiter.isAllowed(userId, apiId);
        assertThat(allowed).isFalse();
    }

    @Test
    void shouldAllowRequestsAfterWindowReset() {
        String userId = "user1";
        String apiId = "api1";
        
        // Fill up the bucket
        IntStream.range(0, 100).forEach(i -> rateLimiter.isAllowed(userId, apiId));
        
        // Move time forward by window duration
        when(timeProvider.getCurrentTimeMillis())
            .thenReturn(Instant.now().plusSeconds(60).toEpochMilli());
        
        boolean allowed = rateLimiter.isAllowed(userId, apiId);
        assertThat(allowed).isTrue();
    }

    @Test
    void shouldHandleConcurrentRequests() throws Exception {
        String userId = "user1";
        String apiId = "api1";
        int numThreads = 10;
        int requestsPerThread = 20;
        
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CompletableFuture<Integer>[] futures = new CompletableFuture[numThreads];
        
        // Launch concurrent requests
        for (int i = 0; i < numThreads; i++) {
            futures[i] = CompletableFuture.supplyAsync(() -> {
                int allowed = 0;
                for (int j = 0; j < requestsPerThread; j++) {
                    if (rateLimiter.isAllowed(userId, apiId)) {
                        allowed++;
                    }
                }
                return allowed;
            }, executor);
        }
        
        // Wait for all threads to complete
        CompletableFuture.allOf(futures).get(5, TimeUnit.SECONDS);
        executor.shutdown();
        
        // Count total allowed requests
        int totalAllowed = 0;
        for (CompletableFuture<Integer> future : futures) {
            totalAllowed += future.get();
        }
        
        // Should not exceed rate limit
        assertThat(totalAllowed).isLessThanOrEqualTo(100);
    }

    @Test
    void shouldHandleMultipleUsersIndependently() {
        String user1 = "user1";
        String user2 = "user2";
        String apiId = "api1";
        
        // Fill up user1's bucket
        IntStream.range(0, 100).forEach(i -> rateLimiter.isAllowed(user1, apiId));
        
        // User2 should still be allowed
        boolean allowed = rateLimiter.isAllowed(user2, apiId);
        assertThat(allowed).isTrue();
    }

    @Test
    void shouldHandleMultipleApisIndependently() {
        String userId = "user1";
        String api1 = "api1";
        String api2 = "api2";
        
        // Fill up api1's bucket
        IntStream.range(0, 100).forEach(i -> rateLimiter.isAllowed(userId, api1));
        
        // API2 should still be allowed
        boolean allowed = rateLimiter.isAllowed(userId, api2);
        assertThat(allowed).isTrue();
    }

    @Test
    void shouldHandleDifferentTiers() {
        rateLimiter.setUserTier("premium_user", "PREMIUM");
        rateLimiter.setUserTier("basic_user", "BASIC");
        
        // Premium user should be allowed more requests
        int premiumAllowed = IntStream.range(0, 200)
            .map(i -> rateLimiter.isAllowed("premium_user", "api1") ? 1 : 0)
            .sum();
            
        int basicAllowed = IntStream.range(0, 200)
            .map(i -> rateLimiter.isAllowed("basic_user", "api1") ? 1 : 0)
            .sum();
            
        assertThat(premiumAllowed).isGreaterThan(basicAllowed);
    }

    @Test
    void shouldHandlePrioritizedEndpoints() {
        rateLimiter.setPriority("critical_api", 1);
        rateLimiter.setPriority("normal_api", 2);
        
        // Fill up the bucket with normal API calls
        IntStream.range(0, 100).forEach(i -> rateLimiter.isAllowed("user1", "normal_api"));
        
        // Critical API should still be allowed some requests
        boolean allowed = rateLimiter.isAllowed("user1", "critical_api");
        assertThat(allowed).isTrue();
    }
}