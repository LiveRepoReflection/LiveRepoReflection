import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedKeyValueStoreTest {

    private DistributedKeyValueStore store;

    @BeforeEach
    public void setUp() {
        // Assume the DistributedKeyValueStore constructor initializes a cluster with default nodes and replication factor.
        store = new DistributedKeyValueStore();
    }

    @Test
    public void testSimplePutGet() {
        boolean putResult = store.put("key1", "value1");
        assertTrue(putResult, "Put operation should succeed");
        String value = store.get("key1");
        assertEquals("value1", value, "Retrieved value should match the stored value");
    }

    @Test
    public void testDelete() {
        store.put("key2", "value2");
        String value = store.get("key2");
        assertEquals("value2", value, "Value must be present before delete");
        boolean deleteResult = store.delete("key2");
        assertTrue(deleteResult, "Delete operation should succeed");
        String deletedValue = store.get("key2");
        assertNull(deletedValue, "After deletion, key should not be present");
    }

    @Test
    public void testGetNonExistentKey() {
        String value = store.get("nonexistent");
        assertNull(value, "Getting a nonexistent key should return null");
    }

    @Test
    public void testDeleteNonExistentKey() {
        boolean deleteResult = store.delete("nonexistent");
        assertFalse(deleteResult, "Deleting a nonexistent key should return false");
    }

    @Test
    public void testOverwriteValue() {
        store.put("key3", "initial");
        String val1 = store.get("key3");
        assertEquals("initial", val1, "Initial value must be correct");
        // Overwrite value
        store.put("key3", "updated");
        String val2 = store.get("key3");
        assertEquals("updated", val2, "Value should be updated with new information");
    }

    @Test
    public void testReplicationAfterNodeFailure() {
        // Insert a key-value pair and simulate node failure
        store.put("replicatedKey", "replicatedValue");
        // Simulate failure of one node; assume the API removeNode(NodeIdentifier) is available.
        // Retrieve a list of active nodes in the system.
        List<String> currentNodes = store.getActiveNodeIds();
        // Fail the first replica node
        if (!currentNodes.isEmpty()) {
            store.removeNode(currentNodes.get(0));
        }
        // The key must still be available because of replication.
        String value = store.get("replicatedKey");
        assertEquals("replicatedValue", value, "Value must still be retrievable after a node failure");
    }

    @Test
    public void testNodeJoinAndRebalance() {
        // Put several keys into store.
        store.put("keyA", "A");
        store.put("keyB", "B");
        store.put("keyC", "C");
        // Add a new node, simulating dynamic scaling.
        store.addNode("newNode");
        // Wait for rebalancing or data migration.
        // (Assuming the implementation ensures rebalance is complete upon addNode call)
        String valueA = store.get("keyA");
        String valueB = store.get("keyB");
        String valueC = store.get("keyC");
        assertEquals("A", valueA, "Value for keyA must remain consistent after node addition");
        assertEquals("B", valueB, "Value for keyB must remain consistent after node addition");
        assertEquals("C", valueC, "Value for keyC must remain consistent after node addition");
    }

    @Test
    @Timeout(10)
    public void testConcurrentAccess() throws InterruptedException, ExecutionException {
        int threadCount = 20;
        int operationsPerThread = 100;
        ExecutorService executorService = Executors.newFixedThreadPool(threadCount);
        List<Callable<Boolean>> tasks = new ArrayList<>();

        // Concurrently put operations.
        for (int i = 0; i < threadCount; i++) {
            final int threadNum = i;
            tasks.add(() -> {
                for (int j = 0; j < operationsPerThread; j++) {
                    String key = "concurrentKey_" + threadNum + "_" + j;
                    boolean result = store.put(key, "value" + j);
                    if (!result) {
                        return false;
                    }
                }
                return true;
            });
        }
        List<Future<Boolean>> futures = executorService.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent put operations should succeed");
        }

        // Concurrently get operations.
        tasks.clear();
        for (int i = 0; i < threadCount; i++) {
            final int threadNum = i;
            tasks.add(() -> {
                for (int j = 0; j < operationsPerThread; j++) {
                    String key = "concurrentKey_" + threadNum + "_" + j;
                    String value = store.get(key);
                    if (value == null || !value.equals("value" + j)) {
                        return false;
                    }
                }
                return true;
            });
        }
        futures = executorService.invokeAll(tasks);
        for (Future<Boolean> future : futures) {
            assertTrue(future.get(), "All concurrent get operations should return correct values");
        }
        executorService.shutdown();
    }

    @Test
    public void testEdgeCaseEmptyKey() {
        // Test behavior when empty key is provided.
        boolean putResult = store.put("", "emptyKey");
        // Depending on design, empty keys might be disallowed.
        // Here we assume put returns false for empty key.
        assertFalse(putResult, "Empty key should not be accepted");
    }

    @Test
    public void testEdgeCaseNullValue() {
        // Test behavior when value is null.
        // Assuming null value is not accepted.
        boolean putResult = store.put("nullValueKey", null);
        assertFalse(putResult, "Null values should not be accepted");
    }
}