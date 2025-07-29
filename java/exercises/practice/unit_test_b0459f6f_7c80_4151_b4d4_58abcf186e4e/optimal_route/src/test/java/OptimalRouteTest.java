package optimal_route;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class OptimalRouteTest {

    // Helper method to create a test graph with nodes and edges.
    private Map<String, List<Edge>> createTestGraph() {
        Map<String, List<Edge>> graph = new HashMap<>();

        // Add edges for a sample graph.
        addEdge(graph, "A", "B", 5.0, 10.0, 1.0, 2.0);  // cost = 10 + 2 = 12
        addEdge(graph, "B", "C", 7.0, 15.0, 1.0, 3.0);  // cost = 15 + 3 = 18
        addEdge(graph, "A", "C", 12.0, 20.0, 1.0, 5.0); // cost = 20 + 5 = 25
        addEdge(graph, "B", "D", 3.0, 5.0, 2.0, 1.0);   // cost = (5 * 2) + 1 = 11
        addEdge(graph, "D", "C", 4.0, 8.0, 1.5, 2.0);   // cost = (8 * 1.5) + 2 = 14

        // Introduce a disconnected node.
        graph.putIfAbsent("E", new ArrayList<>());

        return graph;
    }

    // Utility method to add an edge to the graph.
    private void addEdge(Map<String, List<Edge>> graph, String source, String target, double length, double baseTravelTime, double trafficFactor, double tollPrice) {
        graph.putIfAbsent(source, new ArrayList<>());
        graph.get(source).add(new Edge(target, length, baseTravelTime, trafficFactor, tollPrice));
    }

    // Minimal Edge class used to represent a road segment within the graph.
    public static class Edge {
        public String target;
        public double length;
        public double baseTravelTime;
        public double trafficFactor;
        public double tollPrice;

        public Edge(String target, double length, double baseTravelTime, double trafficFactor, double tollPrice) {
            this.target = target;
            this.length = length;
            this.baseTravelTime = baseTravelTime;
            this.trafficFactor = trafficFactor;
            this.tollPrice = tollPrice;
        }
    }

    @Test
    public void testOptimalRouteDirectVsIndirect() {
        Map<String, List<Edge>> graph = createTestGraph();
        // In this graph, the direct route A -> C has a cost of 25,
        // while the indirect route A -> B -> C has a cost of 12 + 18 = 30.
        OptimalRouteSolver solver = new OptimalRouteSolver(graph);
        List<String> route = solver.findOptimalRoute("A", "C", 30.0);
        List<String> expected = Arrays.asList("A", "C");
        assertEquals(expected, route, "The optimal route should be direct from A to C");
    }

    @Test
    public void testRouteWithAlternatePath() {
        Map<String, List<Edge>> graph = createTestGraph();
        // Remove the direct edge from A to C.
        graph.get("A").removeIf(edge -> edge.target.equals("C"));
        OptimalRouteSolver solver = new OptimalRouteSolver(graph);
        List<String> route = solver.findOptimalRoute("A", "C", 40.0);
        // Now the optimal route should be A -> B -> C.
        List<String> expected = Arrays.asList("A", "B", "C");
        assertEquals(expected, route, "The optimal route should be A -> B -> C after removing direct edge A -> C");
    }

    @Test
    public void testNoRouteWithinMaxTravelTime() {
        Map<String, List<Edge>> graph = createTestGraph();
        OptimalRouteSolver solver = new OptimalRouteSolver(graph);
        // With maxTravelTime set too low, no route from A to C can be found.
        List<String> route = solver.findOptimalRoute("A", "C", 5.0);
        assertTrue(route == null || route.isEmpty(), "Should return null or empty list when no route fits maxTravelTime");
    }

    @Test
    public void testDisconnectedGraph() {
        Map<String, List<Edge>> graph = createTestGraph();
        OptimalRouteSolver solver = new OptimalRouteSolver(graph);
        // Node E is disconnected; hence, no route from A to E exists.
        List<String> route = solver.findOptimalRoute("A", "E", 50.0);
        assertTrue(route == null || route.isEmpty(), "Should return null or empty list when destination is unreachable");
    }

    @Test
    public void testFloatingPointPrecision() {
        Map<String, List<Edge>> graph = createTestGraph();
        // Introduce floating-point values that may affect precision.
        addEdge(graph, "C", "F", 3.5, 7.2, 1.3, 0.8);
        addEdge(graph, "A", "F", 10.0, 20.0, 1.0, 2.0);
        OptimalRouteSolver solver = new OptimalRouteSolver(graph);
        List<String> route = solver.findOptimalRoute("A", "F", 50.0);
        // Evaluate the costs:
        // Direct route A -> F: cost = 20.0 + 2.0 = 22.0
        // Indirect route A -> C -> F: cost = (20.0 + 5.0) + (7.2 * 1.3 + 0.8) ≈ 25.0 + 10.16 = 35.16
        // Thus, the direct route should be optimal.
        List<String> expected = Arrays.asList("A", "F");
        assertEquals(expected, route, "Precision issues should not affect the optimal route calculation");
    }
}