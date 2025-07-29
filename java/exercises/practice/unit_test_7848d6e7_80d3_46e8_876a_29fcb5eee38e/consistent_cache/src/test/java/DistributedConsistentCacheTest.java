import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedConsistentCacheTest {

    private DistributedConsistentCache cache;

    @BeforeEach
    public void setUp() {
        // Create three cache nodes for the cluster
        CacheNode node1 = new CacheNode("node1");
        CacheNode node2 = new CacheNode("node2");
        CacheNode node3 = new CacheNode("node3");
        List<CacheNode> nodes = Arrays.asList(node1, node2, node3);
        // Initialize the cache with replication factor 2
        cache = new DistributedConsistentCache(nodes, 2);
    }

    @Test
    public void testBasicPutAndGet() {
        String key = "key1";
        String value = "testValue";
        cache.put(key, value.getBytes());
        byte[] result = cache.get(key);
        assertNotNull(result, "Expected a non-null value from get()");
        assertEquals(value, new String(result), "The retrieved value should match the written value");
    }

    @Test
    public void testNonExistentKey() {
        String key = "nonexistent";
        byte[] result = cache.get(key);
        assertNull(result, "Expecting null for a key that was never inserted");
    }

    @Test
    public void testEventualConsistency() throws InterruptedException {
        // Put a key and immediately try to get it from a different replica.
        String key = "eventual";
        String value = "consistent";
        cache.put(key, value.getBytes());

        // Wait to allow asynchronous replication to complete.
        Thread.sleep(200);

        byte[] result = cache.get(key);
        assertNotNull(result, "After replication delay, the value should be available");
        assertEquals(value, new String(result), "The retrieved value should be eventually consistent with the written value");
    }

    @Test
    public void testNodeFailureHandling() throws InterruptedException {
        String key = "failKey";
        String value = "backupValue";
        cache.put(key, value.getBytes());

        // Simulate failure of the node that is primarily responsible for the key.
        // The API removeNode is assumed to simulate node failure.
        String failedNodeId = cache.getPrimaryNodeIdForKey(key);
        cache.removeNode(failedNodeId);

        // Wait to allow the system to adjust.
        Thread.sleep(200);

        byte[] result = cache.get(key);
        assertNotNull(result, "Value should be retrievable from a replica even if primary node fails");
        assertEquals(value, new String(result), "The retrieved value should match the original after node failure");
    }

    @Test
    public void testConcurrentAccess() throws InterruptedException, ExecutionException {
        ExecutorService executor = Executors.newFixedThreadPool(10);
        int numTasks = 50;
        Callable<Boolean>[] tasks = new Callable[numTasks];

        // Prepare concurrent put tasks
        for (int i = 0; i < numTasks; i++) {
            final int index = i;
            tasks[i] = () -> {
                String key = "concurrentKey" + index;
                String value = "value" + index;
                cache.put(key, value.getBytes());
                return true;
            };
        }

        List<Future<Boolean>> futures = executor.invokeAll(Arrays.asList(tasks));
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "Concurrent put task should complete successfully");
        }

        // Validate that all values are correctly retrievable
        for (int i = 0; i < numTasks; i++) {
            String key = "concurrentKey" + i;
            String expected = "value" + i;
            byte[] result = cache.get(key);
            assertNotNull(result, "Value for " + key + " should not be null");
            assertEquals(expected, new String(result), "Mismatch for key " + key);
        }

        executor.shutdown();
    }
}