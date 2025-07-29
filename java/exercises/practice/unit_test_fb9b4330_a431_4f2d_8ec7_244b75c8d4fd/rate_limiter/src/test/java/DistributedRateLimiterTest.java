import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatNoException;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class DistributedRateLimiterTest {

    @Mock
    private RateLimiterStorage mockStorage;

    private DistributedRateLimiter rateLimiter;

    @BeforeEach
    public void setUp() {
        // The actual implementation will be created in each test as needed
    }

    @AfterEach
    public void tearDown() {
        if (rateLimiter != null) {
            rateLimiter.close();
        }
    }

    @Test
    public void allowsRequestsWithinLimit() throws Exception {
        // Given
        when(mockStorage.incrementAndCheckLimit(anyString(), anyInt(), anyInt())).thenReturn(true);
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);

        // When
        boolean isAllowed = rateLimiter.isAllowed("client1", 100, 60);

        // Then
        assertThat(isAllowed).isTrue();
        verify(mockStorage).incrementAndCheckLimit("client1", 100, 60);
    }

    @Test
    public void blocksRequestsBeyondLimit() throws Exception {
        // Given
        when(mockStorage.incrementAndCheckLimit(anyString(), anyInt(), anyInt())).thenReturn(false);
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);

        // When
        boolean isAllowed = rateLimiter.isAllowed("client1", 100, 60);

        // Then
        assertThat(isAllowed).isFalse();
        verify(mockStorage).incrementAndCheckLimit("client1", 100, 60);
    }

    @Test
    public void handlesDifferentClientsWithDifferentLimits() throws Exception {
        // Given
        when(mockStorage.incrementAndCheckLimit(eq("client1"), anyInt(), anyInt())).thenReturn(true);
        when(mockStorage.incrementAndCheckLimit(eq("client2"), anyInt(), anyInt())).thenReturn(false);
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);

        // When
        boolean client1Allowed = rateLimiter.isAllowed("client1", 100, 60);
        boolean client2Allowed = rateLimiter.isAllowed("client2", 50, 30);

        // Then
        assertThat(client1Allowed).isTrue();
        assertThat(client2Allowed).isFalse();
        verify(mockStorage).incrementAndCheckLimit("client1", 100, 60);
        verify(mockStorage).incrementAndCheckLimit("client2", 50, 30);
    }

    @Test
    public void gracefullyHandlesStorageFailures() throws Exception {
        // Given
        when(mockStorage.incrementAndCheckLimit(anyString(), anyInt(), anyInt())).thenThrow(new DistributedRateLimiterException("Storage error"));
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);

        // When
        boolean isAllowed = rateLimiter.isAllowed("client1", 100, 60);

        // Then
        // Default behavior should be to allow requests in case of storage failures
        assertThat(isAllowed).isTrue();
        verify(mockStorage).incrementAndCheckLimit("client1", 100, 60);
    }

    @Test
    public void closesStorageOnShutdown() {
        // Given
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);

        // When
        rateLimiter.close();

        // Then
        verify(mockStorage).close();
    }

    @Test
    public void handlesMultipleConcurrentRequests() throws Exception {
        // Given
        int numThreads = 100;
        int maxRequests = 50;
        String clientId = "client1";
        AtomicInteger allowedCounter = new AtomicInteger(0);
        AtomicInteger deniedCounter = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(numThreads);
        ExecutorService executor = Executors.newFixedThreadPool(10);
        
        // Create a real implementation with a simulated storage
        ConcurrentHashMap<String, AtomicInteger> requestCounts = new ConcurrentHashMap<>();
        RateLimiterStorage realStorage = new RateLimiterStorage() {
            @Override
            public boolean incrementAndCheckLimit(String clientId, int maxRequests, int timeWindowInSeconds) {
                AtomicInteger count = requestCounts.computeIfAbsent(clientId, k -> new AtomicInteger(0));
                int currentCount = count.incrementAndGet();
                return currentCount <= maxRequests;
            }

            @Override
            public void close() {
                // No resources to clean up
            }
        };
        
        rateLimiter = new DefaultDistributedRateLimiter(realStorage);
        
        // When
        List<Runnable> tasks = new ArrayList<>();
        for (int i = 0; i < numThreads; i++) {
            tasks.add(() -> {
                try {
                    boolean allowed = rateLimiter.isAllowed(clientId, maxRequests, 60);
                    if (allowed) {
                        allowedCounter.incrementAndGet();
                    } else {
                        deniedCounter.incrementAndGet();
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        tasks.forEach(executor::submit);
        
        // Then
        assertThat(latch.await(5, TimeUnit.SECONDS)).isTrue();
        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.SECONDS);
        
        assertThat(allowedCounter.get()).isEqualTo(maxRequests);
        assertThat(deniedCounter.get()).isEqualTo(numThreads - maxRequests);
        assertThat(allowedCounter.get() + deniedCounter.get()).isEqualTo(numThreads);
    }

    @Test
    public void differentTimeWindowsRespected() throws Exception {
        // Given
        String clientId = "client1";
        int maxRequests = 5;
        int timeWindow1 = 60;  // 60 seconds
        int timeWindow2 = 30;  // 30 seconds
        
        // When/Then
        when(mockStorage.incrementAndCheckLimit(eq(clientId), eq(maxRequests), eq(timeWindow1))).thenReturn(true);
        when(mockStorage.incrementAndCheckLimit(eq(clientId), eq(maxRequests), eq(timeWindow2))).thenReturn(false);
        
        rateLimiter = new DefaultDistributedRateLimiter(mockStorage);
        
        assertThat(rateLimiter.isAllowed(clientId, maxRequests, timeWindow1)).isTrue();
        assertThat(rateLimiter.isAllowed(clientId, maxRequests, timeWindow2)).isFalse();
    }

    @Test
    public void constructorDoesNotThrowException() {
        // Given/When/Then
        assertThatNoException().isThrownBy(() -> {
            rateLimiter = new DefaultDistributedRateLimiter(mockStorage);
        });
    }
}