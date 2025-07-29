import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class OptimalRoutingTest {

    private OptimalRouting optimalRouting;

    @BeforeEach
    public void setup() {
        optimalRouting = new OptimalRouting();
        // Initialize the network with a fixed number of nodes.
        // Assuming the constructor of OptimalRouting takes the number of nodes.
        optimalRouting.initialize(5); // For example, 5 nodes: 0 through 4
    }

    @Test
    public void testBasicPath() {
        // Build a simple network:
        // 0 --10-- 1 --10-- 2 --5-- 3, and a direct but expensive link 0 --30-- 2
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 2, 10);
        optimalRouting.addLink(2, 3, 5);
        optimalRouting.addLink(0, 2, 30);

        List<Integer> expectedPath = Arrays.asList(0, 1, 2, 3);
        List<Integer> actualPath = optimalRouting.findOptimalPath(0, 3);
        assertEquals(expectedPath, actualPath, "The basic optimal path from 0 to 3 should be [0, 1, 2, 3]");
    }

    @Test
    public void testPathWithLatencyUpdate() {
        // Create network:
        // 0 --10-- 1, 1 --20-- 2, 0 --40-- 2.
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 2, 20);
        optimalRouting.addLink(0, 2, 40);

        // Initially, optimal path from 0 to 2 should be via 1.
        List<Integer> expectedPathInitial = Arrays.asList(0, 1, 2);
        List<Integer> actualPathInitial = optimalRouting.findOptimalPath(0, 2);
        assertEquals(expectedPathInitial, actualPathInitial, "Initial optimal path from 0 to 2 should be [0, 1, 2]");

        // Now update the latency on link (0,1) to make it worse.
        optimalRouting.updateLatency(0, 1, 50);

        // Now the direct link (0,2) should be optimal.
        List<Integer> expectedPathAfter = Collections.singletonList(0);
        expectedPathAfter = Arrays.asList(0, 2); // reassign expected path properly
        List<Integer> actualPathAfter = optimalRouting.findOptimalPath(0, 2);
        assertEquals(expectedPathAfter, actualPathAfter, "After updating latency, optimal path from 0 to 2 should be [0, 2]");
    }

    @Test
    public void testPathWithCongestionUpdate() {
        // Build network:
        // 0 --10-- 1 --10-- 2 and 0 --15-- 2
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 2, 10);
        optimalRouting.addLink(0, 2, 15);

        // Initially, optimal path should be [0, 1, 2] (total cost 20) vs [0,2] (15).
        List<Integer> expectedInitial = Arrays.asList(0, 2);
        List<Integer> actualInitial = optimalRouting.findOptimalPath(0, 2);
        assertEquals(expectedInitial, actualInitial, "Initial optimal path from 0 to 2 should be [0, 2]");

        // Now, simulate congestion on the direct link making its cost worse.
        optimalRouting.updateCongestion(0, 2, 2);  // cost becomes 15*2 = 30

        // Now, optimal path should revert to [0, 1, 2] with total cost 10+10 = 20.
        List<Integer> expectedAfterCongestion = Arrays.asList(0, 1, 2);
        List<Integer> actualAfterCongestion = optimalRouting.findOptimalPath(0, 2);
        assertEquals(expectedAfterCongestion, actualAfterCongestion, "After congestion update, optimal path from 0 to 2 should be [0, 1, 2]");
    }

    @Test
    public void testDynamicLinkRemoval() {
        // Build network:
        // 0 --10-- 1 --10-- 2
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 2, 10);

        // The initial optimal path from 0 to 2 is [0, 1, 2]
        List<Integer> expectedPath = Arrays.asList(0, 1, 2);
        List<Integer> actualPath = optimalRouting.findOptimalPath(0, 2);
        assertEquals(expectedPath, actualPath, "Optimal path from 0 to 2 should be [0, 1, 2]");

        // Remove the link that connects 1 and 2.
        optimalRouting.removeLink(1, 2);

        // Now, there should be no path from 0 to 2.
        List<Integer> noPath = optimalRouting.findOptimalPath(0, 2);
        assertTrue(noPath.isEmpty(), "After removal, there should be no path from 0 to 2");
    }

    @Test
    public void testCircularPathHandling() {
        // Build a cycle:
        // 0 --10-- 1, 1 --10-- 2, 2 --10-- 0, and an extra link 2 --5-- 3.
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 2, 10);
        optimalRouting.addLink(2, 0, 10);
        optimalRouting.addLink(2, 3, 5);

        // Optimal path from 0 to 3 should be [0, 1, 2, 3] or [0, 2, 3] depending on the algorithm;
        // but the returned path must not repeat nodes.
        List<Integer> path = optimalRouting.findOptimalPath(0, 3);
        assertNotNull(path, "Path should not be null");
        assertFalse(path.isEmpty(), "Path should not be empty");
        assertEquals(0, (int) path.get(0), "Path should start with the source node 0");
        assertEquals(3, (int) path.get(path.size() - 1), "Path should end with the destination node 3");

        // Verify no duplicate nodes in the path
        for (int i = 0; i < path.size(); i++) {
            for (int j = i + 1; j < path.size(); j++) {
                assertNotEquals(path.get(i), path.get(j), "Path should not contain duplicate nodes");
            }
        }
    }

    @Test
    public void testMultipleOptimalPaths() {
        // Build network:
        // Two potential optimal paths from 0 to 3:
        // Path 1: 0 --10-- 1 --10-- 3 => total cost = 20
        // Path 2: 0 --10-- 2 --10-- 3 => total cost = 20
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(1, 3, 10);
        optimalRouting.addLink(0, 2, 10);
        optimalRouting.addLink(2, 3, 10);

        List<Integer> path = optimalRouting.findOptimalPath(0, 3);

        // The path should start with 0 and end with 3.
        assertFalse(path.isEmpty(), "Path should not be empty");
        assertEquals(0, (int) path.get(0), "Path should start with 0");
        assertEquals(3, (int) path.get(path.size() - 1), "Path should end with 3");

        // The total cost should equal 20.
        int totalCost = 0;
        for (int i = 0; i < path.size() - 1; i++) {
            int cost = optimalRouting.getEffectiveLatency(path.get(i), path.get(i + 1));
            totalCost += cost;
        }
        assertEquals(20, totalCost, "The total cost of the optimal path should be 20");
    }

    @Test
    public void testNoPathAvailable() {
        // Build network with nodes but without connectivity.
        optimalRouting.addLink(0, 1, 10);
        optimalRouting.addLink(2, 3, 10);

        // There is no connection between node 0 and node 3.
        List<Integer> path = optimalRouting.findOptimalPath(0, 3);
        assertTrue(path.isEmpty(), "There should be no path between 0 and 3");
    }
}