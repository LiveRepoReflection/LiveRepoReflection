import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.*;
import java.util.*;

public class ConsistentHashingLoadBalancerTest {

    private ConsistentHashingLoadBalancer loadBalancer;

    @BeforeEach
    public void setUp() {
        // Initialize with 100 virtual nodes per physical node for better distribution
        loadBalancer = new ConsistentHashingLoadBalancer(100);
    }

    @Test
    public void testGetNodeWhenNoServerPresent() {
        String key = "testKey";
        assertNull(loadBalancer.getNode(key));
    }

    @Test
    public void testAddNodeAndRetrieve() {
        loadBalancer.addNode("node1");
        String node = loadBalancer.getNode("key1");
        assertNotNull(node);
        assertEquals("node1", node);
    }

    @Test
    public void testMultipleNodesAssignment() {
        loadBalancer.addNode("node1");
        loadBalancer.addNode("node2");
        loadBalancer.addNode("node3");

        Set<String> validNodes = new HashSet<>(Arrays.asList("node1", "node2", "node3"));
        for (int i = 0; i < 100; i++) {
            String key = "key" + i;
            String assignedNode = loadBalancer.getNode(key);
            assertTrue(validNodes.contains(assignedNode));
        }
    }

    @Test
    public void testRemoveNodeEffect() {
        loadBalancer.addNode("node1");
        loadBalancer.addNode("node2");
        loadBalancer.addNode("node3");

        Map<String, String> assignmentBefore = new HashMap<>();
        for (int i = 0; i < 100; i++) {
            String key = "key" + i;
            assignmentBefore.put(key, loadBalancer.getNode(key));
        }

        loadBalancer.removeNode("node2");

        // After removal, ensure that "node2" is not assigned for any key.
        for (Map.Entry<String, String> entry : assignmentBefore.entrySet()) {
            String key = entry.getKey();
            String assignedNode = loadBalancer.getNode(key);
            assertNotEquals("node2", assignedNode);
        }
    }

    @Test
    public void testGetRingSize() {
        loadBalancer.addNode("node1");
        loadBalancer.addNode("node2");
        // Each node contributes 100 virtual nodes
        assertEquals(200, loadBalancer.getRingSize());
        loadBalancer.removeNode("node1");
        assertEquals(100, loadBalancer.getRingSize());
    }

    @Test
    @Timeout(5)
    public void testConcurrencyInGetNode() throws InterruptedException, ExecutionException {
        loadBalancer.addNode("node1");
        loadBalancer.addNode("node2");
        loadBalancer.addNode("node3");

        int threads = 10;
        int iterationsPerThread = 1000;
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        List<Callable<Void>> tasks = new ArrayList<>();

        for (int i = 0; i < threads; i++) {
            tasks.add(() -> {
                for (int iter = 0; iter < iterationsPerThread; iter++) {
                    String key = "concurrentKey" + ThreadLocalRandom.current().nextInt(10000);
                    String node = loadBalancer.getNode(key);
                    assertNotNull(node);
                }
                return null;
            });
        }

        List<Future<Void>> futures = executor.invokeAll(tasks);
        for (Future<Void> future : futures) {
            future.get();
        }
        executor.shutdown();
    }

    @Test
    public void testVirtualNodeConsistency() {
        loadBalancer.addNode("node1");
        int initialRingSize = loadBalancer.getRingSize();
        assertEquals(100, initialRingSize);

        // Adding the same node again should not increase the ring size (idempotency)
        loadBalancer.addNode("node1");
        int laterRingSize = loadBalancer.getRingSize();
        assertEquals(100, laterRingSize);
    }
}