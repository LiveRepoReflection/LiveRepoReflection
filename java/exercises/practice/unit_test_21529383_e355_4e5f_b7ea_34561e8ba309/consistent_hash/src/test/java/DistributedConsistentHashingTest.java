import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadLocalRandom;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedConsistentHashingTest {
    private DistributedConsistentHashing dch;

    @BeforeEach
    public void setup() {
        // Initialize the consistent hash table with 10 nodes
        dch = new DistributedConsistentHashing(10);
    }

    @Test
    public void testPutAndGet() {
        dch.put("key1", "value1");
        dch.put("key2", "value2");
        dch.put("key3", "value3");

        assertEquals("value1", dch.get("key1"), "Key 'key1' should return 'value1'");
        assertEquals("value2", dch.get("key2"), "Key 'key2' should return 'value2'");
        assertEquals("value3", dch.get("key3"), "Key 'key3' should return 'value3'");
    }

    @Test
    public void testOverwriteValue() {
        dch.put("key1", "value1");
        assertEquals("value1", dch.get("key1"), "Key 'key1' initial value should be 'value1'");
        dch.put("key1", "value2");
        assertEquals("value2", dch.get("key1"), "Key 'key1' should be updated to 'value2'");
    }

    @Test
    public void testGetNonExistentKey() {
        assertNull(dch.get("nonexistent"), "Non-existent key should return null");
    }

    @Test
    public void testAddNode() {
        dch.put("alpha", "A");
        dch.put("beta", "B");
        dch.put("gamma", "C");

        int newNodeId = dch.addNode();
        assertTrue(newNodeId >= 0, "New node ID should be non-negative");

        // After adding a node, existing keys should still be retrievable.
        assertEquals("A", dch.get("alpha"), "Key 'alpha' should return 'A'");
        assertEquals("B", dch.get("beta"), "Key 'beta' should return 'B'");
        assertEquals("C", dch.get("gamma"), "Key 'gamma' should return 'C'");
    }

    @Test
    public void testRemoveNode() {
        dch.put("key1", "value1");
        dch.put("key2", "value2");

        // Remove a node that is expected to exist. For testing purposes, we remove node with id 0.
        dch.removeNode(0);

        // After removal, keys must be accessible via their new responsible nodes.
        assertEquals("value1", dch.get("key1"), "Key 'key1' should return 'value1' after node removal");
        assertEquals("value2", dch.get("key2"), "Key 'key2' should return 'value2' after node removal");
    }

    @Test
    public void testRebalance() {
        dch.put("alpha", "A");
        dch.put("beta", "B");
        dch.put("gamma", "C");
        dch.put("delta", "D");
        dch.put("epsilon", "E");

        // Simulate multiple add and remove operations
        int newNode = dch.addNode();
        dch.removeNode(newNode);
        dch.addNode();
        dch.addNode();

        // Execute rebalance to optimize key distribution
        dch.rebalance();

        // All keys should remain retrievable after rebalancing
        assertEquals("A", dch.get("alpha"), "Key 'alpha' should return 'A' after rebalancing");
        assertEquals("B", dch.get("beta"), "Key 'beta' should return 'B' after rebalancing");
        assertEquals("C", dch.get("gamma"), "Key 'gamma' should return 'C' after rebalancing");
        assertEquals("D", dch.get("delta"), "Key 'delta' should return 'D' after rebalancing");
        assertEquals("E", dch.get("epsilon"), "Key 'epsilon' should return 'E' after rebalancing");
    }

    @Test
    @Timeout(10)
    public void testConcurrency() throws InterruptedException, ExecutionException {
        int numThreads = 50;
        int numOperations = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);

        Callable<Void> writeTask = () -> {
            for (int i = 0; i < numOperations; i++) {
                String key = "key" + ThreadLocalRandom.current().nextInt(0, numOperations);
                String value = "value" + ThreadLocalRandom.current().nextInt(0, numOperations);
                dch.put(key, value);
            }
            return null;
        };

        Callable<Void> readTask = () -> {
            for (int i = 0; i < numOperations; i++) {
                String key = "key" + ThreadLocalRandom.current().nextInt(0, numOperations);
                dch.get(key);
            }
            return null;
        };

        Future<?>[] futures = new Future<?>[numThreads];
        for (int i = 0; i < numThreads; i++) {
            if (i % 2 == 0) {
                futures[i] = executor.submit(writeTask);
            } else {
                futures[i] = executor.submit(readTask);
            }
        }
        for (Future<?> future : futures) {
            future.get();
        }
        executor.shutdown();
    }
}