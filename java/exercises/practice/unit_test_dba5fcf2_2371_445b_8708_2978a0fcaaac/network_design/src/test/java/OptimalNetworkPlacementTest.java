import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;

import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class OptimalNetworkPlacementTest {

    private OptimalNetworkPlacement solver;

    @BeforeEach
    public void setUp() {
        solver = new OptimalNetworkPlacement();
    }

    // Helper method to compute the total latency of the returned network.
    private int computeTotalLatency(List<List<Integer>> network, int[][] distances) {
        int total = 0;
        for (List<Integer> edge : network) {
            int i = edge.get(0);
            int j = edge.get(1);
            total += distances[i][j];
        }
        return total;
    }

    // Helper method to compute the degree (number of connections) for each node.
    private Map<Integer, Integer> computeDegrees(List<List<Integer>> network) {
        Map<Integer, Integer> degreeMap = new HashMap<>();
        for (List<Integer> edge : network) {
            int a = edge.get(0);
            int b = edge.get(1);
            degreeMap.put(a, degreeMap.getOrDefault(a, 0) + 1);
            degreeMap.put(b, degreeMap.getOrDefault(b, 0) + 1);
        }
        return degreeMap;
    }

    // Helper method to collect all nodes present in the network.
    private Set<Integer> collectSelectedNodes(List<List<Integer>> network) {
        Set<Integer> nodes = new HashSet<>();
        for (List<Integer> edge : network) {
            nodes.add(edge.get(0));
            nodes.add(edge.get(1));
        }
        return nodes;
    }

    @Test
    @DisplayName("Test Simple Valid Network")
    public void testValidSimpleNetwork() {
        int numDataCenters = 3;
        int[][] distances = {
            {0, 10, 20},
            {10, 0, 15},
            {20, 15, 0}
        };
        int minConnectivity = 2;
        int maxLatency = 100;
        
        List<List<Integer>> result = solver.designNetwork(numDataCenters, distances, minConnectivity, maxLatency);
        
        // Verify that a non-empty network is returned.
        assertFalse(result.isEmpty(), "Result should not be empty for a valid network configuration.");
        
        // Check each connection is a valid pair of distinct nodes.
        for (List<Integer> edge : result) {
            assertEquals(2, edge.size(), "Each connection must have exactly two data center indices.");
            assertNotEquals(edge.get(0), edge.get(1), "Connection cannot have the same node twice.");
            assertTrue(edge.get(0) >= 0 && edge.get(0) < numDataCenters, "Node index out of bounds.");
            assertTrue(edge.get(1) >= 0 && edge.get(1) < numDataCenters, "Node index out of bounds.");
        }
        
        // Verify each selected data center meets the minimum connectivity.
        Map<Integer, Integer> degrees = computeDegrees(result);
        for (int node : collectSelectedNodes(result)) {
            assertTrue(degrees.getOrDefault(node, 0) >= minConnectivity, 
                       "Node " + node + " does not satisfy the minimum connectivity requirement.");
        }
        
        // Verify the total latency does not exceed the maximum latency.
        int totalLatency = computeTotalLatency(result, distances);
        assertTrue(totalLatency <= maxLatency, "Total latency exceeds the maximum allowed limit.");
    }

    @Test
    @DisplayName("Test No Valid Network Found")
    public void testNoValidNetwork() {
        int numDataCenters = 3;
        int[][] distances = {
            {0, 5, 8},
            {5, 0, 7},
            {8, 7, 0}
        };
        int minConnectivity = 3; // Cannot be satisfied since each node can only connect to at most 2 other nodes.
        int maxLatency = 50;
        
        List<List<Integer>> result = solver.designNetwork(numDataCenters, distances, minConnectivity, maxLatency);
        
        // The result should be empty in an impossible configuration.
        assertTrue(result.isEmpty(), "Result should be empty when no valid network configuration exists.");
    }

    @Test
    @DisplayName("Test Latency Constraint")
    public void testLatencyConstraint() {
        int numDataCenters = 4;
        int[][] distances = {
            {0, 100, 100, 100},
            {100, 0, 100, 100},
            {100, 100, 0, 100},
            {100, 100, 100, 0}
        };
        int minConnectivity = 2;
        int maxLatency = 150;  // Too low to allow any valid configuration.
        
        List<List<Integer>> result = solver.designNetwork(numDataCenters, distances, minConnectivity, maxLatency);
        
        // The network should be empty because the latency constraint cannot be met.
        assertTrue(result.isEmpty(), "Result should be empty when the latency constraint cannot be satisfied.");
    }

    @Test
    @DisplayName("Test Edge Case with Zero Distances")
    public void testEdgeCaseAllZeros() {
        int numDataCenters = 5;
        int[][] distances = {
            {0, 0, 0, 0, 0},
            {0, 0, 0, 0, 0},
            {0, 0, 0, 0, 0},
            {0, 0, 0, 0, 0},
            {0, 0, 0, 0, 0}
        };
        int minConnectivity = 1;
        int maxLatency = 0;
        
        List<List<Integer>> result = solver.designNetwork(numDataCenters, distances, minConnectivity, maxLatency);
        
        // Validate that the latency is zero and connectivity holds.
        int totalLatency = computeTotalLatency(result, distances);
        assertEquals(0, totalLatency, "Total latency should be zero when all distances are zero.");
        
        Map<Integer, Integer> degrees = computeDegrees(result);
        for (int node : collectSelectedNodes(result)) {
            assertTrue(degrees.getOrDefault(node, 0) >= minConnectivity, 
                       "Node " + node + " does not meet the minimum connectivity requirement.");
        }
    }

    @Test
    @DisplayName("Test Complex Scenario with Multiple Valid Approaches")
    public void testMultipleValidApproaches() {
        int numDataCenters = 6;
        int[][] distances = {
            {0, 10, 20, 30, 40, 50},
            {10, 0, 15, 25, 35, 45},
            {20, 15, 0, 12, 22, 32},
            {30, 25, 12, 0, 18, 28},
            {40, 35, 22, 18, 0, 14},
            {50, 45, 32, 28, 14, 0}
        };
        int minConnectivity = 2;
        int maxLatency = 120;
        
        List<List<Integer>> result = solver.designNetwork(numDataCenters, distances, minConnectivity, maxLatency);
        
        // Verify that a valid solution is provided.
        assertFalse(result.isEmpty(), "Result should not be empty for a complex valid network configuration.");
        
        // Each connection must be a valid pair.
        for (List<Integer> edge : result) {
            assertEquals(2, edge.size(), "Each connection must consist of exactly two data centers.");
            int a = edge.get(0);
            int b = edge.get(1);
            assertNotEquals(a, b, "Edge cannot connect a data center to itself.");
            assertTrue(a >= 0 && a < numDataCenters, "Node index out of bounds.");
            assertTrue(b >= 0 && b < numDataCenters, "Node index out of bounds.");
        }
        
        // Verify connectivity for each selected data center.
        Map<Integer, Integer> degrees = computeDegrees(result);
        for (int node : collectSelectedNodes(result)) {
            assertTrue(degrees.getOrDefault(node, 0) >= minConnectivity, 
                       "Node " + node + " does not meet the minimum connectivity requirement.");
        }
        
        // Ensure the sum of distances for all network links satisfies the latency constraint.
        int totalLatency = computeTotalLatency(result, distances);
        assertTrue(totalLatency <= maxLatency, "Total latency exceeds the allowed limit.");
    }
}