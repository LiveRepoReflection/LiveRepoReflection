package distributed_cache;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.RepeatedTest;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.*;

class DistributedCacheTest {

    private DistributedCache cache;

    @BeforeEach
    void setup() {
        // Initialize the distributed cache with 5 nodes, replication factor of 3, and a small memory limit (in bytes)
        // Note: The memory limit is assumed to be handled internally in the cache implementation.
        cache = new DistributedCache(5, 3, 1024 * 10); // 10 KB limit for testing LRU eviction
    }

    @Test
    void testBasicPutGetDelete() {
        String key = "testKey";
        byte[] value = "testValue".getBytes(StandardCharsets.UTF_8);
        cache.put(key, value, 1000);
        byte[] result = cache.get(key);
        assertNotNull(result, "Value should not be null after put");
        assertTrue(Arrays.equals(value, result), "Retrieved value must be equal to inserted value");

        cache.delete(key);
        assertNull(cache.get(key), "Value should be null after deletion");
    }

    @Test
    void testExpiryMechanism() throws InterruptedException {
        String key = "expiringKey";
        byte[] value = "expiringValue".getBytes(StandardCharsets.UTF_8);
        // Set expiry to 1 second
        cache.put(key, value, 1);
        byte[] result = cache.get(key);
        assertNotNull(result, "Value should be available immediately after put");

        // Wait for expiry (adding an extra buffer)
        Thread.sleep(1200);
        assertNull(cache.get(key), "Value should be expired and return null");
    }

    @Test
    void testReplicationAndFaultTolerance() {
        String key = "replicatedKey";
        byte[] value = "replicatedValue".getBytes(StandardCharsets.UTF_8);
        cache.put(key, value, 1000);

        // In a replicated system, simulate failure of one replica.
        // Assume cache has a method to simulate node failure.
        cache.simulateNodeFailure(0);
        byte[] result = cache.get(key);
        assertNotNull(result, "Value should still be available despite node failure");
        assertTrue(Arrays.equals(value, result), "Value should match after node failure");

        // Recover the failed node for continued tests
        cache.recoverNode(0);
        result = cache.get(key);
        assertNotNull(result, "Value should be available after recovery");
        assertTrue(Arrays.equals(value, result), "Value should be repaired after recovery (read repair)");
    }

    @Test
    void testConsistentHashingOnNodeAddition() {
        // Insert multiple keys into the cache
        for (int i = 0; i < 50; i++) {
            String key = "key_" + i;
            byte[] value = ("value_" + i).getBytes(StandardCharsets.UTF_8);
            cache.put(key, value, 1000);
        }

        // Simulate adding a new node to the cache
        int oldNodeCount = cache.getNodeCount();
        cache.addNode();
        int newNodeCount = cache.getNodeCount();
        assertEquals(oldNodeCount + 1, newNodeCount, "Node count should increase by one after adding a node");

        // Verify that all keys are still accessible with correct value
        for (int i = 0; i < 50; i++) {
            String key = "key_" + i;
            byte[] expected = ("value_" + i).getBytes(StandardCharsets.UTF_8);
            byte[] result = cache.get(key);
            assertNotNull(result, "Value for key " + key + " should still be available after adding node");
            assertTrue(Arrays.equals(expected, result), "Value for key " + key + " should be correct after rebalancing");
        }
    }

    @Test
    void testLRUEviction() {
        // Insert keys until the memory limit is likely exceeded.
        // Note: This test assumes that the cache employs an LRU-based eviction when memory limit is reached.
        int count = 0;
        while (true) {
            String key = "evictKey_" + count;
            // Create a value of 1KB to quickly reach memory limit.
            byte[] value = new byte[1024];
            Arrays.fill(value, (byte) (count % 128));
            cache.put(key, value, 1000);
            byte[] result = cache.get(key);
            if (result == null) {
                // The just inserted key has been evicted which means limit has been reached.
                break;
            }
            count++;
            // Safeguard to prevent infinite loop in case eviction doesn't trigger.
            if (count > 20) {
                break;
            }
        }

        // Ensure that some keys are evicted due to memory limits.
        int evictedCount = 0;
        for (int i = 0; i < count; i++) {
            String key = "evictKey_" + i;
            if (cache.get(key) == null) {
                evictedCount++;
            }
        }
        assertTrue(evictedCount > 0, "There should be evicted keys when memory limit is reached");
    }

    @Test
    @Timeout(10)
    void testConcurrentOperations() throws InterruptedException {
        int threadCount = 10;
        int operationsPerThread = 100;
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(threadCount);

        // Each thread performs a series of put, get, and delete operations concurrently.
        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            executor.execute(() -> {
                for (int j = 0; j < operationsPerThread; j++) {
                    String key = "concurrentKey_" + (threadId * operationsPerThread + j);
                    byte[] value = ("concurrentValue_" + j).getBytes(StandardCharsets.UTF_8);
                    cache.put(key, value, 5);
                    byte[] retrieved = cache.get(key);
                    if (retrieved != null) {
                        // Occasionally delete the key
                        if (j % 10 == 0) {
                            cache.delete(key);
                            assertNull(cache.get(key), "Value should be deleted and return null");
                        } else {
                            assertTrue(Arrays.equals(value, retrieved), "Concurrent put/get should work correctly");
                        }
                    }
                }
                latch.countDown();
            });
        }
        latch.await();
        executor.shutdown();
    }

    @Test
    void testReadRepairMechanism() {
        // Simulate a scenario where replicas might become inconsistent.
        String key = "repairKey";
        byte[] initialValue = "initial".getBytes(StandardCharsets.UTF_8);
        cache.put(key, initialValue, 1000);

        // Artificially simulate a stale replica scenario.
        // Assume there is a method to manually corrupt a replica for testing.
        cache.corruptReplica(key, "stale".getBytes(StandardCharsets.UTF_8));

        // When get is called, the read repair mechanism should detect and fix the stale replica.
        byte[] repairedValue = cache.get(key);
        assertNotNull(repairedValue, "Value should be available after repair");
        assertTrue(Arrays.equals(initialValue, repairedValue), "Read repair should fix replica to initial value");
    }
}