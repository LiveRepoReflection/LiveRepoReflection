import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class RateLimitTest {

    private DistributedRateLimiter rateLimiter;
    private RateLimiterConfig config;

    @Mock
    private DistributedCache mockCache;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        config = new RateLimiterConfig();
        config.setCache(mockCache);
        rateLimiter = new DistributedRateLimiter(config);
    }

    @Nested
    @DisplayName("Rule Management Tests")
    class RuleManagementTests {
        
        @Test
        @DisplayName("Adding a new rule should be successful")
        void testAddRule() {
            // Arrange
            String ruleId = "rule1";
            String target = "user123";
            int limit = 100;
            int window = 60;
            
            // Act
            rateLimiter.addRule(ruleId, target, limit, window);
            
            // Assert
            verify(mockCache).setRule(eq(ruleId), any(RateLimitRule.class));
        }
        
        @Test
        @DisplayName("Updating an existing rule should be successful")
        void testUpdateRule() {
            // Arrange
            String ruleId = "rule1";
            int newLimit = 200;
            int newWindow = 120;
            
            when(mockCache.ruleExists(ruleId)).thenReturn(true);
            
            // Act
            boolean result = rateLimiter.updateRule(ruleId, newLimit, newWindow);
            
            // Assert
            assertTrue(result);
            verify(mockCache).updateRule(eq(ruleId), eq(newLimit), eq(newWindow));
        }
        
        @Test
        @DisplayName("Updating a non-existent rule should return false")
        void testUpdateNonExistentRule() {
            // Arrange
            String ruleId = "nonExistentRule";
            int newLimit = 200;
            int newWindow = 120;
            
            when(mockCache.ruleExists(ruleId)).thenReturn(false);
            
            // Act
            boolean result = rateLimiter.updateRule(ruleId, newLimit, newWindow);
            
            // Assert
            assertFalse(result);
            verify(mockCache, never()).updateRule(anyString(), anyInt(), anyInt());
        }
        
        @Test
        @DisplayName("Removing an existing rule should be successful")
        void testRemoveRule() {
            // Arrange
            String ruleId = "rule1";
            when(mockCache.ruleExists(ruleId)).thenReturn(true);
            
            // Act
            boolean result = rateLimiter.removeRule(ruleId);
            
            // Assert
            assertTrue(result);
            verify(mockCache).removeRule(ruleId);
        }
        
        @Test
        @DisplayName("Removing a non-existent rule should return false")
        void testRemoveNonExistentRule() {
            // Arrange
            String ruleId = "nonExistentRule";
            when(mockCache.ruleExists(ruleId)).thenReturn(false);
            
            // Act
            boolean result = rateLimiter.removeRule(ruleId);
            
            // Assert
            assertFalse(result);
            verify(mockCache, never()).removeRule(anyString());
        }
    }
    
    @Nested
    @DisplayName("Rate Limiting Tests")
    class RateLimitingTests {
        
        @Test
        @DisplayName("Request should be allowed when under the limit")
        void testRequestAllowedUnderLimit() {
            // Arrange
            String targetId = "user123";
            String ruleId = "rule1";
            
            when(mockCache.incrementRequestCount(targetId, ruleId)).thenReturn(5);
            when(mockCache.getRule(ruleId)).thenReturn(new RateLimitRule(ruleId, targetId, 10, 60));
            
            // Act
            boolean result = rateLimiter.isAllowed(targetId, ruleId);
            
            // Assert
            assertTrue(result);
        }
        
        @Test
        @DisplayName("Request should be denied when over the limit")
        void testRequestDeniedOverLimit() {
            // Arrange
            String targetId = "user123";
            String ruleId = "rule1";
            
            when(mockCache.incrementRequestCount(targetId, ruleId)).thenReturn(15);
            when(mockCache.getRule(ruleId)).thenReturn(new RateLimitRule(ruleId, targetId, 10, 60));
            
            // Act
            boolean result = rateLimiter.isAllowed(targetId, ruleId);
            
            // Assert
            assertFalse(result);
            verify(mockCache).decrementRequestCount(targetId, ruleId);
        }
        
        @Test
        @DisplayName("Request should be denied when rule does not exist")
        void testRequestDeniedRuleNotFound() {
            // Arrange
            String targetId = "user123";
            String ruleId = "nonExistentRule";
            
            when(mockCache.getRule(ruleId)).thenReturn(null);
            
            // Act
            boolean result = rateLimiter.isAllowed(targetId, ruleId);
            
            // Assert
            assertFalse(result);
            verify(mockCache, never()).incrementRequestCount(anyString(), anyString());
        }
        
        @Test
        @DisplayName("Request should be denied when target doesn't match rule target")
        void testRequestDeniedTargetMismatch() {
            // Arrange
            String targetId = "user456";
            String ruleId = "rule1";
            
            when(mockCache.getRule(ruleId)).thenReturn(new RateLimitRule(ruleId, "user123", 10, 60));
            
            // Act
            boolean result = rateLimiter.isAllowed(targetId, ruleId);
            
            // Assert
            assertFalse(result);
            verify(mockCache, never()).incrementRequestCount(anyString(), anyString());
        }
        
        @Test
        @DisplayName("Wildcard rule should apply to any target")
        void testWildcardRuleAllowsAnyTarget() {
            // Arrange
            String targetId = "user789";
            String ruleId = "wildcardRule";
            
            when(mockCache.getRule(ruleId)).thenReturn(new RateLimitRule(ruleId, "*", 10, 60));
            when(mockCache.incrementRequestCount(targetId, ruleId)).thenReturn(5);
            
            // Act
            boolean result = rateLimiter.isAllowed(targetId, ruleId);
            
            // Assert
            assertTrue(result);
        }
    }
    
    @Nested
    @DisplayName("Concurrency Tests")
    class ConcurrencyTests {
        
        private DistributedRateLimiter realRateLimiter;
        private InMemoryDistributedCache inMemoryCache;
        
        @BeforeEach
        void setUp() {
            inMemoryCache = new InMemoryDistributedCache();
            RateLimiterConfig config = new RateLimiterConfig();
            config.setCache(inMemoryCache);
            realRateLimiter = new DistributedRateLimiter(config);
            
            // Add a test rule
            realRateLimiter.addRule("testRule", "*", 100, 60);
        }
        
        @Test
        @DisplayName("Concurrent requests should correctly respect the rate limit")
        void testConcurrentRequests() throws InterruptedException {
            // Arrange
            int numThreads = 50;
            int requestsPerThread = 10;
            ExecutorService executorService = Executors.newFixedThreadPool(numThreads);
            CountDownLatch latch = new CountDownLatch(numThreads);
            AtomicInteger allowedCount = new AtomicInteger(0);
            
            // Act
            for (int i = 0; i < numThreads; i++) {
                executorService.submit(() -> {
                    try {
                        for (int j = 0; j < requestsPerThread; j++) {
                            if (realRateLimiter.isAllowed("user1", "testRule")) {
                                allowedCount.incrementAndGet();
                            }
                        }
                    } finally {
                        latch.countDown();
                    }
                });
            }
            
            latch.await(10, TimeUnit.SECONDS);
            executorService.shutdown();
            
            // Assert
            assertEquals(100, allowedCount.get(), "Should allow exactly 100 requests (the rule limit)");
        }
        
        @Test
        @DisplayName("Multiple rules for the same target should function correctly")
        void testMultipleRulesForSameTarget() {
            // Arrange
            String targetId = "user1";
            realRateLimiter.addRule("restrictiveRule", targetId, 5, 60);
            realRateLimiter.addRule("permissiveRule", targetId, 20, 60);
            
            // Act & Assert
            // Test restrictive rule
            for (int i = 0; i < 5; i++) {
                assertTrue(realRateLimiter.isAllowed(targetId, "restrictiveRule"), 
                           "Should allow first 5 requests with restrictive rule");
            }
            assertFalse(realRateLimiter.isAllowed(targetId, "restrictiveRule"), 
                        "Should deny 6th request with restrictive rule");
            
            // Test permissive rule (separately)
            for (int i = 0; i < 20; i++) {
                assertTrue(realRateLimiter.isAllowed(targetId, "permissiveRule"), 
                           "Should allow first 20 requests with permissive rule");
            }
            assertFalse(realRateLimiter.isAllowed(targetId, "permissiveRule"), 
                        "Should deny 21st request with permissive rule");
        }
    }

    // In-memory implementation of DistributedCache for testing
    private static class InMemoryDistributedCache implements DistributedCache {
        private final Map<String, RateLimitRule> rules = new ConcurrentHashMap<>();
        private final Map<String, AtomicInteger> requestCounts = new ConcurrentHashMap<>();
        
        @Override
        public RateLimitRule getRule(String ruleId) {
            return rules.get(ruleId);
        }
        
        @Override
        public void setRule(String ruleId, RateLimitRule rule) {
            rules.put(ruleId, rule);
        }
        
        @Override
        public boolean ruleExists(String ruleId) {
            return rules.containsKey(ruleId);
        }
        
        @Override
        public void updateRule(String ruleId, int limit, int window) {
            RateLimitRule rule = rules.get(ruleId);
            if (rule != null) {
                rules.put(ruleId, new RateLimitRule(ruleId, rule.getTarget(), limit, window));
            }
        }
        
        @Override
        public void removeRule(String ruleId) {
            rules.remove(ruleId);
        }
        
        @Override
        public int incrementRequestCount(String targetId, String ruleId) {
            String key = targetId + ":" + ruleId;
            AtomicInteger counter = requestCounts.computeIfAbsent(key, k -> new AtomicInteger(0));
            return counter.incrementAndGet();
        }
        
        @Override
        public void decrementRequestCount(String targetId, String ruleId) {
            String key = targetId + ":" + ruleId;
            AtomicInteger counter = requestCounts.get(key);
            if (counter != null) {
                counter.decrementAndGet();
            }
        }
    }
}