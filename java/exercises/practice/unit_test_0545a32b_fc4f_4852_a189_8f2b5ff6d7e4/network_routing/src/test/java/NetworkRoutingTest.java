import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;
import java.util.*;

public class NetworkRoutingTest {

    private NetworkRouting network;

    @Before
    public void setup() {
        // Create initial network links:
        // (0, 1) with costs [1, 2]
        // (1, 2) with costs [3, 4]
        // (0, 2) with costs [5, 6]
        List<Link> initialLinks = new ArrayList<>();
        initialLinks.add(new Link(0, 1, new int[]{1, 2}));
        initialLinks.add(new Link(1, 2, new int[]{3, 4}));
        initialLinks.add(new Link(0, 2, new int[]{5, 6}));

        // Initialize the network with default weights [0.5, 0.5]
        network = new NetworkRouting(initialLinks, new double[]{0.5, 0.5});
    }

    @Test
    public void testInitialOptimalPath() {
        // Query the optimal path from node 0 to node 2 with weights [0.5, 0.5]
        List<Integer> expectedPath = Arrays.asList(0, 1, 2);
        List<Integer> actualPath = network.getOptimalPath(0, 2, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testAddLink() {
        // Add new link (2, 3) with costs [1, 1]
        network.addLink(2, 3, new int[]{1, 1});
        List<Integer> expectedPath = Arrays.asList(0, 1, 2, 3);
        List<Integer> actualPath = network.getOptimalPath(0, 3, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testRemoveLink() {
        // Remove link (1, 2) and check optimal path from 0 to 2
        network.removeLink(1, 2);
        List<Integer> expectedPath = Arrays.asList(0, 2);
        List<Integer> actualPath = network.getOptimalPath(0, 2, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testCostChange() {
        // Change cost of link (0, 2) from [5, 6] to [2, 2] with weights [0.5, 0.5]
        network.changeLinkCost(0, 2, new int[]{2, 2});
        // Direct link (0,2) now has a total cost of (2*0.5 + 2*0.5 = 2),
        // which should be lower than the cost via (0,1,2)
        List<Integer> expectedPath = Arrays.asList(0, 2);
        List<Integer> actualPath = network.getOptimalPath(0, 2, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testWeightsChange() {
        // Change the default weights to [0.2, 0.8]--
        // Recalculate costs for links:
        // (0,1): 1*0.2 + 2*0.8 = 1.8
        // (1,2): 3*0.2 + 4*0.8 = 3.8
        // (0,2): 5*0.2 + 6*0.8 = 5.8
        // Optimal path from 0 to 2 should become [0,1,2]
        network.updateWeights(new double[]{0.2, 0.8});
        List<Integer> expectedPath = Arrays.asList(0, 1, 2);
        List<Integer> actualPath = network.getOptimalPath(0, 2, null); // null reuses the updated weights
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testNoPathExists() {
        // Remove links to disconnect node 0 from node 2
        network.removeLink(0, 1);
        network.removeLink(0, 2);
        List<Integer> expectedPath = Collections.emptyList();
        List<Integer> actualPath = network.getOptimalPath(0, 2, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }

    @Test
    public void testComplexUpdates() {
        // Perform a series of operations:
        // 1. Add link (2, 3) with costs [1, 1]
        // 2. Add link (3, 4) with costs [2, 2]
        // 3. Remove link (1, 2)
        // 4. Change cost of link (0, 2) to [4, 4]
        network.addLink(2, 3, new int[]{1, 1});
        network.addLink(3, 4, new int[]{2, 2});
        network.removeLink(1, 2);
        network.changeLinkCost(0, 2, new int[]{4, 4});
        // For weights [0.5, 0.5]:
        // Cost for (0,2) = 4*0.5 + 4*0.5 = 4
        // Cost for (2,3) = 1*0.5 + 1*0.5 = 1
        // Cost for (3,4) = 2*0.5 + 2*0.5 = 2
        // Total expected cost for path [0,2,3,4] = 4 + 1 + 2 = 7
        List<Integer> expectedPath = Arrays.asList(0, 2, 3, 4);
        List<Integer> actualPath = network.getOptimalPath(0, 4, new double[]{0.5, 0.5});
        assertEquals(expectedPath, actualPath);
    }
}