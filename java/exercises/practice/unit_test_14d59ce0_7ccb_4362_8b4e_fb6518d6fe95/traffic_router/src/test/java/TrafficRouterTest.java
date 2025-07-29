import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TrafficRouterTest {

    @Test
    public void testBasicRoute() {
        // Create a basic graph with nodes: 1, 2, 3
        // Edges: 1->2 (base time 10), 2->3 (base time 20), 1->3 (base time 40)
        // Expected best route from 1 to 3: [1, 2, 3] with total time 30.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10, 1.0));
        edges.add(new Edge(2, 3, 20, 1.0));
        edges.add(new Edge(1, 3, 40, 1.0));

        Map<Integer, Coordinate> coordinates = new HashMap<>();
        coordinates.put(1, new Coordinate(0, 0));
        coordinates.put(2, new Coordinate(1, 0));
        coordinates.put(3, new Coordinate(2, 0));

        TrafficRouter router = new TrafficRouter(edges, coordinates);
        RouteResult result = router.findRoute(1, 3);

        List<Integer> expectedRoute = Arrays.asList(1, 2, 3);
        assertNotNull(result, "Expected a valid route result");
        assertEquals(expectedRoute, result.getRoute(), "The route should be [1, 2, 3]");
        assertEquals(30.0, result.getTravelTime(), 1e-6, "Total travel time should be 30.0 seconds");
    }

    @Test
    public void testTrafficUpdateAffectsRoute() {
        // Create a graph with two possible routes:
        // Route1: 1->2 (10) and 2->3 (20) total = 30 seconds
        // Route2: Direct 1->3 (25) total = 25 seconds
        // Initially, the best route should be [1, 3] with 25 seconds.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10, 1.0));
        edges.add(new Edge(2, 3, 20, 1.0));
        edges.add(new Edge(1, 3, 25, 1.0));

        Map<Integer, Coordinate> coordinates = new HashMap<>();
        coordinates.put(1, new Coordinate(0, 0));
        coordinates.put(2, new Coordinate(1, 0));
        coordinates.put(3, new Coordinate(2, 0));

        TrafficRouter router = new TrafficRouter(edges, coordinates);
        RouteResult initialResult = router.findRoute(1, 3);

        List<Integer> expectedInitialRoute = Arrays.asList(1, 3);
        assertNotNull(initialResult, "Expected a valid initial route result");
        assertEquals(expectedInitialRoute, initialResult.getRoute(), "Initially, the best route should be [1, 3]");
        assertEquals(25.0, initialResult.getTravelTime(), 1e-6, "Total travel time should be 25.0 seconds");

        // Apply a traffic update to the direct route 1->3: congestion factor becomes 2.0 so time = 25*2 = 50
        router.updateTraffic(1, 3, 2.0);
        RouteResult updatedResult = router.findRoute(1, 3);

        List<Integer> expectedUpdatedRoute = Arrays.asList(1, 2, 3);
        assertNotNull(updatedResult, "Expected a valid updated route result");
        assertEquals(expectedUpdatedRoute, updatedResult.getRoute(), "After update, the best route should be [1, 2, 3]");
        assertEquals(30.0, updatedResult.getTravelTime(), 1e-6, "Total travel time should be 30.0 seconds");
    }

    @Test
    public void testDisconnectedGraph() {
        // Create a graph where nodes 1 and 2 are connected, and node 3 is isolated.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 15, 1.0));

        Map<Integer, Coordinate> coordinates = new HashMap<>();
        coordinates.put(1, new Coordinate(0, 0));
        coordinates.put(2, new Coordinate(1, 1));
        coordinates.put(3, new Coordinate(5, 5));

        TrafficRouter router = new TrafficRouter(edges, coordinates);
        // Querying a route from node 1 to node 3 should return null (no route exists)
        RouteResult result = router.findRoute(1, 3);
        assertNull(result, "Expected no valid route for disconnected nodes");
    }

    @Test
    public void testInvalidNodes() {
        // Create a simple graph with valid nodes 1 and 2
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10, 1.0));

        Map<Integer, Coordinate> coordinates = new HashMap<>();
        coordinates.put(1, new Coordinate(0, 0));
        coordinates.put(2, new Coordinate(1, 0));

        TrafficRouter router = new TrafficRouter(edges, coordinates);
        // Querying a route with an invalid node (e.g., node 99) should throw an exception
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            router.findRoute(1, 99);
        });
        String expectedMessage = "Invalid node ID";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.contains(expectedMessage), "Exception message should indicate an invalid node ID");
    }

    @Test
    public void testMultipleEqualRoutes() {
        // Create a graph with two equal cost routes:
        // Route1: 1->2 (10) and 2->4 (10) => total = 20
        // Route2: 1->3 (10) and 3->4 (10) => total = 20
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10, 1.0));
        edges.add(new Edge(2, 4, 10, 1.0));
        edges.add(new Edge(1, 3, 10, 1.0));
        edges.add(new Edge(3, 4, 10, 1.0));

        Map<Integer, Coordinate> coordinates = new HashMap<>();
        coordinates.put(1, new Coordinate(0, 0));
        coordinates.put(2, new Coordinate(1, 1));
        coordinates.put(3, new Coordinate(1, -1));
        coordinates.put(4, new Coordinate(2, 0));

        TrafficRouter router = new TrafficRouter(edges, coordinates);
        RouteResult result = router.findRoute(1, 4);

        assertNotNull(result, "Expected a valid route result");
        List<Integer> route = result.getRoute();
        assertEquals(20.0, result.getTravelTime(), 1e-6, "Total travel time should be 20.0 seconds");
        // Validate that the route starts with 1 and ends with 4.
        assertEquals(1, route.get(0), "Route should start with node 1");
        assertEquals(4, route.get(route.size() - 1), "Route should end with node 4");
        // Check that the route has exactly three nodes.
        assertEquals(3, route.size(), "The route should contain exactly three nodes");
    }
}