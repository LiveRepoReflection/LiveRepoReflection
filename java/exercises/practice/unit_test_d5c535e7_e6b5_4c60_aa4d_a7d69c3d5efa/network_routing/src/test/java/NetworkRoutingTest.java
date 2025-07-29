import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class NetworkRoutingTest {
    private NetworkRouting router;

    @BeforeEach
    public void setUp() {
        // Initialize with 5 servers and some initial links
        List<int[]> initialLinks = Arrays.asList(
            new int[]{0, 1, 5},   // server 0 to server 1 with latency 5
            new int[]{1, 2, 10},  // server 1 to server 2 with latency 10
            new int[]{2, 3, 15},  // server 2 to server 3 with latency 15
            new int[]{0, 4, 20},  // server 0 to server 4 with latency 20
            new int[]{3, 4, 10}   // server 3 to server 4 with latency 10
        );
        router = new NetworkRouting(5, initialLinks);
    }

    @Test
    public void testBasicRouting() {
        // Test routing from server 0 to server 3
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertNotNull(result);
        assertEquals(30, result.getTotalLatency()); // 0->1->2->3 = 5+10+15 = 30
        assertArrayEquals(new int[]{0, 1, 2, 3}, result.getPath());
    }

    @Test
    public void testRoutingToSelf() {
        // Test routing from a server to itself
        NetworkRouting.RoutingResult result = router.findOptimalPath(2, 2);
        assertNotNull(result);
        assertEquals(0, result.getTotalLatency()); // No movement, so latency is 0
        assertArrayEquals(new int[]{2}, result.getPath());
    }

    @Test
    public void testNoPathExists() {
        // Create a disconnected network
        List<int[]> disconnectedLinks = Arrays.asList(
            new int[]{0, 1, 5},
            new int[]{2, 3, 10}
        );
        NetworkRouting disconnectedRouter = new NetworkRouting(4, disconnectedLinks);
        
        // Test routing between disconnected servers
        NetworkRouting.RoutingResult result = disconnectedRouter.findOptimalPath(0, 3);
        assertNull(result.getPath());
        assertEquals(Double.POSITIVE_INFINITY, result.getTotalLatency());
    }

    @Test
    public void testAddLink() {
        // Add a new link that creates a shorter path
        router.addLink(0, 3, 8);
        
        // Test routing from server 0 to server 3 (should now use the direct link)
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertEquals(8, result.getTotalLatency()); // Direct path: 0->3 = 8
        assertArrayEquals(new int[]{0, 3}, result.getPath());
    }

    @Test
    public void testRemoveLink() {
        // Remove a critical link in the path
        router.removeLink(1, 2);
        
        // Test routing from server 0 to server 3 (should now go via server 4)
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertEquals(30, result.getTotalLatency()); // 0->4->3 = 20+10 = 30
        assertArrayEquals(new int[]{0, 4, 3}, result.getPath());
    }

    @Test
    public void testUpdateLatency() {
        // Update latency of a link in the optimal path
        router.updateLatency(0, 1, 25);
        
        // Test routing from server 0 to server 3 (should now go via server 4)
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertEquals(30, result.getTotalLatency()); // 0->4->3 = 20+10 = 30
        assertArrayEquals(new int[]{0, 4, 3}, result.getPath());
    }

    @Test
    public void testLargeNetwork() {
        // Create a larger network to test scalability
        int nodeCount = 100;
        List<int[]> largeNetworkLinks = new ArrayList<>();
        
        // Create a ring topology
        for (int i = 0; i < nodeCount - 1; i++) {
            largeNetworkLinks.add(new int[]{i, i + 1, 1});
        }
        largeNetworkLinks.add(new int[]{nodeCount - 1, 0, 1}); // Close the ring
        
        // Add some cross links
        for (int i = 0; i < nodeCount / 2; i++) {
            largeNetworkLinks.add(new int[]{i, i + nodeCount / 2, 5});
        }
        
        NetworkRouting largeRouter = new NetworkRouting(nodeCount, largeNetworkLinks);
        
        // Test routing across the network
        NetworkRouting.RoutingResult result = largeRouter.findOptimalPath(0, nodeCount / 2);
        assertNotNull(result);
        assertTrue(result.getTotalLatency() <= 5); // Either direct cross link or around half the ring
    }

    @Test
    public void testMultipleUpdates() {
        // Perform multiple updates and verify routing results
        router.addLink(1, 3, 8);
        router.updateLatency(0, 1, 3);
        router.removeLink(2, 3);
        
        // Test routing from server 0 to server 3 (should now go 0->1->3)
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertEquals(11, result.getTotalLatency()); // 0->1->3 = 3+8 = 11
        assertArrayEquals(new int[]{0, 1, 3}, result.getPath());
    }

    @Test
    public void testNetworkPartition() {
        // Remove all links to server 3
        router.removeLink(2, 3);
        router.removeLink(3, 4);
        
        // Test routing to now-isolated server 3
        NetworkRouting.RoutingResult result = router.findOptimalPath(0, 3);
        assertNull(result.getPath());
        assertEquals(Double.POSITIVE_INFINITY, result.getTotalLatency());
    }

    @Test
    public void testAlternativePaths() {
        // Create a network with multiple paths of same total latency
        List<int[]> multiPathLinks = Arrays.asList(
            new int[]{0, 1, 10},
            new int[]{1, 3, 10},
            new int[]{0, 2, 10},
            new int[]{2, 3, 10}
        );
        NetworkRouting multiPathRouter = new NetworkRouting(4, multiPathLinks);
        
        // Both 0->1->3 and 0->2->3 have same latency (20)
        NetworkRouting.RoutingResult result = multiPathRouter.findOptimalPath(0, 3);
        assertEquals(20, result.getTotalLatency());
        
        // The actual path returned could be either one
        boolean validPath = Arrays.equals(result.getPath(), new int[]{0, 1, 3}) || 
                           Arrays.equals(result.getPath(), new int[]{0, 2, 3});
        assertTrue(validPath);
    }

    @Test
    public void testPathThroughMultipleNodes() {
        // Create a linear network to test long paths
        List<int[]> linearLinks = new ArrayList<>();
        int nodeCount = 10;
        
        for (int i = 0; i < nodeCount - 1; i++) {
            linearLinks.add(new int[]{i, i + 1, 1});
        }
        
        NetworkRouting linearRouter = new NetworkRouting(nodeCount, linearLinks);
        
        // Test routing from one end to the other
        NetworkRouting.RoutingResult result = linearRouter.findOptimalPath(0, nodeCount - 1);
        assertEquals(nodeCount - 1, result.getTotalLatency());
        assertEquals(nodeCount, result.getPath().length);
        
        // Verify the path goes through each node in sequence
        int[] expectedPath = new int[nodeCount];
        for (int i = 0; i < nodeCount; i++) {
            expectedPath[i] = i;
        }
        assertArrayEquals(expectedPath, result.getPath());
    }
}