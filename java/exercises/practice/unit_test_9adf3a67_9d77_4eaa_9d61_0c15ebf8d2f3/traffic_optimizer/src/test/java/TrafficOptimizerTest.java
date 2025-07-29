import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class TrafficOptimizerTest {

    // A small epsilon for comparing double values
    private static final double EPSILON = 1e-6;
    // A value to represent infinity for our computations.
    private static final double INF = 1e12;

    /**
     * Helper method to compute the average shortest travel time
     * between all ordered pairs of critical locations in the graph.
     * The graph is represented by an edge list where each int[] is of size 3 ([from, to, travelTime]).
     */
    private double computeAverageTravelTime(int numNodes, List<int[]> edges, List<Integer> criticalLocations) {
        double[][] dist = new double[numNodes][numNodes];
        // Initialize distances
        for (int i = 0; i < numNodes; i++) {
            Arrays.fill(dist[i], INF);
            dist[i][i] = 0;
        }
        // Fill in the edge weights; if multiple edges exist, choose the minimum.
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            double weight = edge[2];
            dist[u][v] = Math.min(dist[u][v], weight);
        }
        // Floyd-Warshall algorithm to compute all pairs shortest paths.
        for (int k = 0; k < numNodes; k++) {
            for (int i = 0; i < numNodes; i++) {
                for (int j = 0; j < numNodes; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        // Compute average for all ordered pairs (u, v) where u != v of the critical locations.
        double sum = 0;
        int count = 0;
        for (int i = 0; i < criticalLocations.size(); i++) {
            for (int j = 0; j < criticalLocations.size(); j++) {
                if (i == j)
                    continue;
                int u = criticalLocations.get(i);
                int v = criticalLocations.get(j);
                sum += dist[u][v];
                count++;
            }
        }
        return (count == 0) ? INF : sum / count;
    }

    /**
     * Applies the candidate's chosen traffic light placements on a cloned edge list.
     * For each chosen placement (u, v), it finds one matching edge (if exists) and reduces its travel time
     * by the reductionPercentage.
     */
    private List<int[]> applyTrafficLights(List<int[]> originalEdges, List<int[]> placements, double reductionPercentage) {
        // Clone the edge list so as not to modify the original
        List<int[]> modifiedEdges = new ArrayList<>();
        for (int[] edge : originalEdges) {
            modifiedEdges.add(Arrays.copyOf(edge, edge.length));
        }
        // For each placement, update one matching edge.
        for (int[] placement : placements) {
            int uChoice = placement[0];
            int vChoice = placement[1];
            for (int[] edge : modifiedEdges) {
                if (edge[0] == uChoice && edge[1] == vChoice) {
                    // Apply the reduction on travel time if not already applied.
                    edge[2] = (int) Math.floor(edge[2] * (1 - reductionPercentage));
                    // Only update one instance per placement.
                    break;
                }
            }
        }
        return modifiedEdges;
    }

    /**
     * Validates that every chosen placement exists in the list of edges.
     * Each placement should match at least one edge in the provided edge list.
     */
    private void validatePlacementsExist(List<int[]> placements, List<int[]> edges) {
        for (int[] placement : placements) {
            boolean exists = false;
            for (int[] edge : edges) {
                if (edge[0] == placement[0] && edge[1] == placement[1]) {
                    exists = true;
                    break;
                }
            }
            assertTrue(exists, "Placement edge (" + placement[0] + ", " + placement[1] + ") does not exist in the graph.");
        }
    }

    /**
     * Test with the sample example provided in the problem description.
     */
    @Test
    public void testSampleExample() {
        int numNodes = 5;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        edges.add(new int[]{0, 2, 15});
        edges.add(new int[]{1, 3, 12});
        edges.add(new int[]{2, 3, 8});
        edges.add(new int[]{3, 4, 5});
        List<Integer> criticalLocations = Arrays.asList(0, 3, 4);
        int numTrafficLights = 1;
        double reductionPercentage = 0.2;

        TrafficOptimizer optimizer = new TrafficOptimizer();
        List<int[]> result = optimizer.optimizeTraffic(numNodes, edges, criticalLocations, numTrafficLights, reductionPercentage);

        // Check that the result is not null and contains the correct number of placements.
        assertNotNull(result, "Resulting placements should not be null.");
        assertEquals(numTrafficLights, result.size(), "The number of placements returned is incorrect.");
        // Validate that each placement corresponds to an edge in the original graph.
        validatePlacementsExist(result, edges);

        // Compute baseline average travel time.
        double baselineAvg = computeAverageTravelTime(numNodes, edges, criticalLocations);
        // Apply modifications based on candidate placements.
        List<int[]> modifiedEdges = applyTrafficLights(edges, result, reductionPercentage);
        double optimizedAvg = computeAverageTravelTime(numNodes, modifiedEdges, criticalLocations);

        // Assert that the optimized average travel time is lower than the baseline.
        assertTrue(optimizedAvg < baselineAvg - EPSILON, "Optimized average travel time should be lower than baseline.");
    }

    /**
     * Test with a graph having multiple candidate placements and multiple traffic lights.
     */
    @Test
    public void testMultipleTrafficLights() {
        int numNodes = 6;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 12});
        edges.add(new int[]{0, 2, 15});
        edges.add(new int[]{1, 3, 10});
        edges.add(new int[]{2, 3, 5});
        edges.add(new int[]{3, 4, 8});
        edges.add(new int[]{4, 5, 7});
        edges.add(new int[]{2, 5, 20});
        List<Integer> criticalLocations = Arrays.asList(0, 3, 5);
        int numTrafficLights = 2;
        double reductionPercentage = 0.25;

        TrafficOptimizer optimizer = new TrafficOptimizer();
        List<int[]> result = optimizer.optimizeTraffic(numNodes, edges, criticalLocations, numTrafficLights, reductionPercentage);

        assertNotNull(result, "Resulting placements should not be null.");
        assertEquals(numTrafficLights, result.size(), "The number of placements returned is incorrect.");
        validatePlacementsExist(result, edges);

        double baselineAvg = computeAverageTravelTime(numNodes, edges, criticalLocations);
        List<int[]> modifiedEdges = applyTrafficLights(edges, result, reductionPercentage);
        double optimizedAvg = computeAverageTravelTime(numNodes, modifiedEdges, criticalLocations);

        assertTrue(optimizedAvg < baselineAvg - EPSILON, "Optimized average travel time should be improved over baseline.");
    }

    /**
     * Test with a graph that is not fully connected.
     * In this scenario, some critical nodes are unreachable, so the baseline and optimized
     * averages should account for infinite travel time.
     */
    @Test
    public void testNonConnectedGraph() {
        int numNodes = 4;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        // No edge connecting component of node 2 and 3 with 0 and 1.
        edges.add(new int[]{2, 3, 5});
        List<Integer> criticalLocations = Arrays.asList(0, 2);
        int numTrafficLights = 1;
        double reductionPercentage = 0.3;

        TrafficOptimizer optimizer = new TrafficOptimizer();
        List<int[]> result = optimizer.optimizeTraffic(numNodes, edges, criticalLocations, numTrafficLights, reductionPercentage);

        // Even though the graph is disconnected, the optimizer should return valid placements (if any)
        assertNotNull(result, "Resulting placements should not be null.");
        // In a disconnected graph, the average travel time is INF so an improvement is not measurable.
        // We only verify that the placements returned (if any) exist in the given edge list.
        validatePlacementsExist(result, edges);
    }

    /**
     * Test with a graph that contains multiple edges between the same nodes.
     */
    @Test
    public void testMultipleEdgesBetweenNodes() {
        int numNodes = 4;
        List<int[]> edges = new ArrayList<>();
        // Two edges from 0 to 1 with different weights.
        edges.add(new int[]{0, 1, 20});
        edges.add(new int[]{0, 1, 15});
        edges.add(new int[]{1, 2, 10});
        edges.add(new int[]{2, 3, 5});
        List<Integer> criticalLocations = Arrays.asList(0, 3);
        int numTrafficLights = 1;
        double reductionPercentage = 0.5;

        TrafficOptimizer optimizer = new TrafficOptimizer();
        List<int[]> result = optimizer.optimizeTraffic(numNodes, edges, criticalLocations, numTrafficLights, reductionPercentage);

        assertNotNull(result, "Resulting placements should not be null.");
        assertEquals(numTrafficLights, result.size(), "The number of placements returned is incorrect.");
        validatePlacementsExist(result, edges);

        double baselineAvg = computeAverageTravelTime(numNodes, edges, criticalLocations);
        List<int[]> modifiedEdges = applyTrafficLights(edges, result, reductionPercentage);
        double optimizedAvg = computeAverageTravelTime(numNodes, modifiedEdges, criticalLocations);

        assertTrue(optimizedAvg < baselineAvg - EPSILON, "Optimized average travel time should be improved over baseline.");
    }

    /**
     * Test with a graph that contains self-loops.
     */
    @Test
    public void testGraphWithSelfLoops() {
        int numNodes = 3;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 0, 5});  // self-loop at node 0
        edges.add(new int[]{0, 1, 10});
        edges.add(new int[]{1, 2, 8});
        edges.add(new int[]{2, 2, 3});  // self-loop at node 2
        List<Integer> criticalLocations = Arrays.asList(0, 2);
        int numTrafficLights = 1;
        double reductionPercentage = 0.4;

        TrafficOptimizer optimizer = new TrafficOptimizer();
        List<int[]> result = optimizer.optimizeTraffic(numNodes, edges, criticalLocations, numTrafficLights, reductionPercentage);

        assertNotNull(result, "Resulting placements should not be null.");
        assertEquals(numTrafficLights, result.size(), "The number of placements returned is incorrect.");
        validatePlacementsExist(result, edges);

        double baselineAvg = computeAverageTravelTime(numNodes, edges, criticalLocations);
        List<int[]> modifiedEdges = applyTrafficLights(edges, result, reductionPercentage);
        double optimizedAvg = computeAverageTravelTime(numNodes, modifiedEdges, criticalLocations);

        // Self-loops do not affect the route between different nodes.
        assertTrue(optimizedAvg < baselineAvg - EPSILON, "Optimized average travel time should be improved over baseline.");
    }
}