import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class NetworkRoutingTest {

    private NetworkRouting routing;

    @BeforeEach
    public void setUp() {
        // Default network with 5 nodes for general tests
        routing = new NetworkRouting(5);
    }

    @Test
    public void testNoPath() {
        // Create a network with 3 nodes and no connections
        NetworkRouting nr = new NetworkRouting(3);
        // No path exists between 0 and 1
        assertEquals(-1, nr.findKthSmallestPath(0, 1, 1));
    }

    @Test
    public void testDirectEdge() {
        // Network with 2 nodes and a single direct edge
        NetworkRouting nr = new NetworkRouting(2);
        nr.addConnection(0, 1, 10);
        assertEquals(10, nr.findKthSmallestPath(0, 1, 1));
        // No second path exists
        assertEquals(-1, nr.findKthSmallestPath(0, 1, 2));
    }

    @Test
    public void testMultipleParallelEdges() {
        // Network with 2 nodes and two parallel edges
        NetworkRouting nr = new NetworkRouting(2);
        nr.addConnection(0, 1, 5);
        nr.addConnection(0, 1, 7);
        // First smallest path latency should be the lower one
        assertEquals(5, nr.findKthSmallestPath(0, 1, 1));
        // Second smallest path latency should be the next one even if different route is not available
        assertEquals(7, nr.findKthSmallestPath(0, 1, 2));
        // Third path does not exist
        assertEquals(-1, nr.findKthSmallestPath(0, 1, 3));
    }

    @Test
    public void testCyclePaths() {
        // Create a network with cycle: 0 -> 1 -> 2 -> 0 and an extra edge 0 -> 2
        NetworkRouting nr = new NetworkRouting(3);
        nr.addConnection(0, 1, 2);
        nr.addConnection(1, 2, 3);
        nr.addConnection(2, 0, 1);
        nr.addConnection(0, 2, 10);
        
        // Expected paths from 0 to 2:
        // Path A: 0 -> 1 -> 2 = 2 + 3 = 5
        // Path B: 0 -> 2 = 10
        // Path C: 0 -> 1 -> 2 -> 0 -> 1 -> 2 = 5 + (cycle: 1->2->0->1->2, but note the cycle used: 2 -> 0 (1) + 0 -> 1 (2) + 1 -> 2 (3)) = 5 + 6 = 11
        // Although further cycles exist, for k up to 3 we can expect the following order:
        assertEquals(5, nr.findKthSmallestPath(0, 2, 1));
        assertEquals(10, nr.findKthSmallestPath(0, 2, 2));
        assertEquals(11, nr.findKthSmallestPath(0, 2, 3));
    }

    @Test
    public void testRemoveConnection() {
        // Network with 2 nodes and two parallel edges, then remove one
        NetworkRouting nr = new NetworkRouting(2);
        nr.addConnection(0, 1, 5);
        nr.addConnection(0, 1, 7);
        
        // Confirm both paths exist
        assertEquals(5, nr.findKthSmallestPath(0, 1, 1));
        assertEquals(7, nr.findKthSmallestPath(0, 1, 2));

        // Remove one connection with latency 5
        nr.removeConnection(0, 1, 5);
        // Now the smallest (and only) path should be the one with latency 7
        assertEquals(7, nr.findKthSmallestPath(0, 1, 1));
        // No second path exists after removal
        assertEquals(-1, nr.findKthSmallestPath(0, 1, 2));
    }

    @Test
    public void testComplexGraph() {
        // Build a network with 5 nodes and multiple routes including a cycle.
        // Graph structure:
        // 0 -> 1 (latency 1)
        // 1 -> 2 (latency 1)
        // 2 -> 3 (latency 1)
        // 3 -> 4 (latency 1)
        // 0 -> 2 (latency 2)
        // 1 -> 3 (latency 2)
        // 2 -> 4 (latency 2)
        // 4 -> 0 (latency 1) forming a cycle
        NetworkRouting nr = new NetworkRouting(5);
        nr.addConnection(0, 1, 1);
        nr.addConnection(1, 2, 1);
        nr.addConnection(2, 3, 1);
        nr.addConnection(3, 4, 1);
        nr.addConnection(0, 2, 2);
        nr.addConnection(1, 3, 2);
        nr.addConnection(2, 4, 2);
        nr.addConnection(4, 0, 1);
        
        // There are many paths from 0 to 4 with equal total latency.
        // Some possible paths (all with latency 4):
        // A: 0 -> 1 -> 2 -> 3 -> 4 = 1 + 1 + 1 + 1 = 4
        // B: 0 -> 1 -> 3 -> 4 = 1 + 2 + 1 = 4
        // C: 0 -> 2 -> 3 -> 4 = 2 + 1 + 1 = 4
        // D: 0 -> 1 -> 2 -> 4 = 1 + 1 + 2 = 4
        // E: 0 -> 2 -> 4 = 2 + 2 = 4
        // We expect that for any k from 1 to 5, the latency returned is 4.
        for (int k = 1; k <= 5; k++) {
            assertEquals(4, nr.findKthSmallestPath(0, 4, k));
        }
        // For a k beyond available simple paths, the cycle can be used.
        // For example, one path including a cycle might be:
        // 0 -> 1 -> 2 -> 3 -> 4 -> 0 -> 1 -> 2 -> 3 -> 4 with latency 4 + (cycle: 4->0 (1) + 0->1 (1) + 1->2 (1) + 2->3 (1) + 3->4 (1)) = 4 + 5 = 9.
        // So, k = 6 should return 9.
        assertEquals(9, nr.findKthSmallestPath(0, 4, 6));
    }
}