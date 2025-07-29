import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Set;

public class NetworkLatencyTest {
    private NetworkLatency network;

    @BeforeEach
    public void setUp() {
        network = new NetworkLatency(5); // Initialize with 5 nodes
    }

    @Test
    public void testInitialEmptyNetwork() {
        assertEquals(-1, network.getMinLatency(0, 1));
        assertEquals(Set.of(0), network.getNodesReachableWithinLatency(0, 0));
    }

    @Test
    public void testAddLinkAndBasicPath() {
        network.addLink(0, 1, 10);
        network.addLink(1, 2, 20);
        assertEquals(10, network.getMinLatency(0, 1));
        assertEquals(30, network.getMinLatency(0, 2));
    }

    @Test
    public void testMultiplePaths() {
        network.addLink(0, 1, 10);
        network.addLink(0, 2, 30);
        network.addLink(1, 2, 10);
        assertEquals(20, network.getMinLatency(0, 2));
    }

    @Test
    public void testUpdateLink() {
        network.addLink(0, 1, 10);
        network.addLink(0, 1, 5); // Update existing link
        assertEquals(5, network.getMinLatency(0, 1));
    }

    @Test
    public void testRemoveLink() {
        network.addLink(0, 1, 10);
        network.removeLink(0, 1);
        assertEquals(-1, network.getMinLatency(0, 1));
    }

    @Test
    public void testReachableNodes() {
        network.addLink(0, 1, 10);
        network.addLink(1, 2, 20);
        network.addLink(2, 3, 30);
        assertEquals(Set.of(0, 1, 2), network.getNodesReachableWithinLatency(0, 40));
    }

    @Test
    public void testSelfLoop() {
        network.addLink(0, 0, 5);
        assertEquals(0, network.getMinLatency(0, 0));
    }

    @Test
    public void testDisconnectedGraph() {
        network.addLink(0, 1, 10);
        network.addLink(2, 3, 10);
        assertEquals(-1, network.getMinLatency(0, 3));
    }

    @Test
    public void testInvalidNodeIds() {
        assertThrows(IllegalArgumentException.class, () -> network.addLink(-1, 0, 10));
        assertThrows(IllegalArgumentException.class, () -> network.addLink(0, 5, 10));
        assertThrows(IllegalArgumentException.class, () -> network.getMinLatency(0, 5));
    }

    @Test
    public void testNegativeLatency() {
        assertThrows(IllegalArgumentException.class, () -> network.addLink(0, 1, -1));
    }

    @Test
    public void testLargeNetworkPerformance() {
        int largeNodeCount = 1000;
        NetworkLatency largeNetwork = new NetworkLatency(largeNodeCount);
        
        // Create a chain of nodes
        for (int i = 0; i < largeNodeCount - 1; i++) {
            largeNetwork.addLink(i, i + 1, 1);
        }
        
        // Should handle this efficiently
        assertEquals(largeNodeCount - 1, largeNetwork.getMinLatency(0, largeNodeCount - 1));
    }
}