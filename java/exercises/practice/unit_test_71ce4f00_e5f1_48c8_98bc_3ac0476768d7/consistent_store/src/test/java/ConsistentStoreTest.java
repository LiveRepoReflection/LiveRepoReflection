import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.*;

public class ConsistentStoreTest {

    private ConsistentStore store;

    @BeforeEach
    public void setUp() {
        // Initialize the store with a replication factor of 3 and 10 virtual nodes per physical node.
        store = new ConsistentStore(3, 10);
        // Add initial nodes to the cluster.
        store.addNode("Node1");
        store.addNode("Node2");
        store.addNode("Node3");
    }

    @AfterEach
    public void tearDown() {
        // Reset the store if necessary.
        store.shutdown();
    }

    @Test
    public void testBasicPutGet() {
        store.put("key1", "value1");
        String result = store.get("key1");
        assertEquals("value1", result, "The value retrieved should be 'value1'");
    }

    @Test
    public void testUpdateValue() {
        store.put("key2", "initial");
        assertEquals("initial", store.get("key2"), "Initial value mismatch");
        store.put("key2", "updated");
        String updatedValue = store.get("key2");
        assertEquals("updated", updatedValue, "Updated value mismatch");
    }

    @Test
    public void testDelete() {
        store.put("key3", "value3");
        assertNotNull(store.get("key3"), "Value should exist before deletion");
        boolean deleted = store.delete("key3");
        assertTrue(deleted, "Delete should return true for successful deletion");
        assertNull(store.get("key3"), "Value should be null after deletion");
    }

    @Test
    public void testNonExistentKey() {
        assertNull(store.get("nonexistent"), "Non-existent key should return null");
        assertFalse(store.delete("nonexistent"), "Delete on non-existent key should return false");
    }

    @Test
    public void testNodeJoin() {
        store.put("key4", "value4");
        assertEquals("value4", store.get("key4"), "Value before node join should be accessible");
        // Join a new node into the cluster.
        store.addNode("Node4");
        // Verify that the existing key is still retrievable after rehashing.
        assertEquals("value4", store.get("key4"), "Value should remain accessible after node join");
    }

    @Test
    public void testNodeLeave() {
        store.put("key5", "value5");
        assertEquals("value5", store.get("key5"), "Value should be accessible before node removal");
        // Remove a node from the cluster.
        store.removeNode("Node2");
        // Keys should be redistributed and remain accessible.
        assertEquals("value5", store.get("key5"), "Value should remain accessible after node removal");
    }

    @Test
    public void testReplicationConsistency() {
        // Put a key-value pair and simulate a node failure.
        store.put("key6", "value6");
        // Simulate failure of one node.
        store.failNode("Node1");
        // Due to replication, the value should still be retrievable.
        assertEquals("value6", store.get("key6"), "Replication should allow retrieval after one node failure");

        // Recover the failed node and then simulate failure of two nodes.
        store.recoverNode("Node1");
        store.failNode("Node2");
        store.failNode("Node3");

        // If the replication factor is compromised, expect the get operation to throw a runtime exception.
        Exception exception = assertThrows(RuntimeException.class, () -> {
            store.get("key6");
        });
        String expectedMessage = "Insufficient replicas available";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.contains(expectedMessage), "Exception message should indicate replication failure");
    }

    @Test
    public void testConcurrentAccess() throws InterruptedException, ExecutionException {
        int numberOfThreads = 10;
        int operationsPerThread = 100;
        ExecutorService executor = Executors.newFixedThreadPool(numberOfThreads);
        List<Future<?>> futures = new ArrayList<>();

        for (int i = 0; i < numberOfThreads; i++) {
            final int threadId = i;
            futures.add(executor.submit(() -> {
                for (int j = 0; j < operationsPerThread; j++) {
                    String key = "concurrentKey" + ((threadId * operationsPerThread) + j);
                    store.put(key, "value" + j);
                    String val = store.get(key);
                    assertNotNull(val, "Value should not be null immediately after put");
                    store.put(key, "updated" + j);
                    String updatedVal = store.get(key);
                    assertEquals("updated" + j, updatedVal, "Updated value mismatch in concurrent access");
                    boolean deleted = store.delete(key);
                    assertTrue(deleted, "Delete should succeed");
                    assertNull(store.get(key), "Value should be null after deletion");
                }
            }));
        }

        for (Future<?> future : futures) {
            future.get();
        }
        executor.shutdown();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS), "Executor did not shut down within the expected time");
    }

    @Test
    public void testMultipleValidOperations() {
        // Insert multiple key-value pairs.
        Map<String, String> keyValues = new HashMap<>();
        for (int i = 0; i < 50; i++) {
            keyValues.put("multiKey" + i, "value" + i);
        }
        for (Map.Entry<String, String> entry : keyValues.entrySet()) {
            store.put(entry.getKey(), entry.getValue());
        }
        // Verify that all inserted values are retrievable.
        for (Map.Entry<String, String> entry : keyValues.entrySet()) {
            String retrieved = store.get(entry.getKey());
            assertEquals(entry.getValue(), retrieved, "Retrieved value should match the stored value");
        }
        // Delete half of the keys.
        for (int i = 0; i < 25; i++) {
            store.delete("multiKey" + i);
        }
        // Check deletion and retention.
        for (int i = 0; i < 25; i++) {
            assertNull(store.get("multiKey" + i), "Value should be null after deletion");
        }
        for (int i = 25; i < 50; i++) {
            assertNotNull(store.get("multiKey" + i), "Value should still be retrievable");
        }
    }
}