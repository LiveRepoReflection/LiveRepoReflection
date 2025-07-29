package route_optimizer;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class OptimalRoutePlannerTest {

    private OptimalRoutePlanner planner;

    @BeforeEach
    public void setUp() {
        planner = new OptimalRoutePlanner();
    }

    // Helper class to hold edge data for constructing graphs in tests.
    private static class EdgeData {
        String from;
        String to;
        double cost;
        int time;

        EdgeData(String from, String to, double cost, int time) {
            this.from = from;
            this.to = to;
            this.cost = cost;
            this.time = time;
        }
    }

    // Helper method to construct a graph with given cities and edges.
    private Graph createGraph(String depot, List<String> cities, List<EdgeData> edges) {
        Graph graph = new Graph();
        // Add all cities to the graph.
        for (String city : cities) {
            graph.addCity(city);
        }
        // Validate depot has been added.
        if (!cities.contains(depot)) {
            graph.addCity(depot);
        }
        // Add specified edges.
        for (EdgeData ed : edges) {
            graph.addEdge(ed.from, ed.to, ed.cost, ed.time);
        }
        return graph;
    }

    @Test
    public void testSingleRoute() {
        // Scenario: A simple graph with depot A and one destination B.
        String depot = "A";
        List<String> cities = Arrays.asList("A", "B");
        List<EdgeData> edges = Arrays.asList(
            new EdgeData("A", "B", 5.0, 10),
            new EdgeData("B", "A", 5.0, 10)
        );

        Graph graph = createGraph(depot, cities, edges);
        Map<String, Integer> demand = new HashMap<>();
        demand.put("B", 50); // Demand for city B is 50 units

        int vehicleCapacity = 100;
        int maxDuration = 30;
        double costMultiplier = 1.0;

        List<Route> routes = planner.planRoutes(graph, demand, depot, vehicleCapacity, maxDuration, costMultiplier);

        assertNotNull(routes, "Routes list should not be null");
        assertEquals(1, routes.size(), "Expected single route for one destination");

        Route route = routes.get(0);
        List<String> expectedSequence = Arrays.asList("A", "B", "A");
        assertEquals(expectedSequence, route.getCitySequence(), "Route should start and end at depot and visit B");

        assertEquals(50, route.getTotalDelivered(), "Total delivered should match the demand for B");

        int expectedTime = 10 + 10;
        assertEquals(expectedTime, route.getTotalTime(), "Total transit time should equal the sum of outgoing and return times");

        double expectedCost = (5.0 + 5.0) * costMultiplier;
        assertEquals(expectedCost, route.getTotalCost(), 0.0001, "Total cost should be computed correctly with cost multiplier");
    }

    @Test
    public void testMultipleVehicles() {
        // Scenario: Multiple vehicles are needed to deliver due to vehicle capacity limits.
        String depot = "A";
        List<String> cities = Arrays.asList("A", "B", "C");
        List<EdgeData> edges = Arrays.asList(
            new EdgeData("A", "B", 4.0, 8),
            new EdgeData("B", "A", 4.0, 8),
            new EdgeData("A", "C", 6.0, 12),
            new EdgeData("C", "A", 6.0, 12)
        );

        Graph graph = createGraph(depot, cities, edges);
        Map<String, Integer> demand = new HashMap<>();
        demand.put("B", 120); // Demand exceeds a single vehicle's capacity.
        demand.put("C", 80);

        int vehicleCapacity = 100;
        int maxDuration = 30;
        double costMultiplier = 1.0;

        List<Route> routes = planner.planRoutes(graph, demand, depot, vehicleCapacity, maxDuration, costMultiplier);

        assertNotNull(routes, "Routes list should not be null");
        // Check that each route respects the vehicle capacity and time constraints.
        int totalDeliveredB = 0;
        int totalDeliveredC = 0;
        for (Route r : routes) {
            assertTrue(r.getTotalDelivered() <= vehicleCapacity, "A route's delivered load must not exceed vehicle capacity");
            assertTrue(r.getTotalTime() <= maxDuration, "A route's total time must not exceed maximum duration");

            if (r.getCitySequence().contains("B")) {
                totalDeliveredB += r.getDeliveredForCity("B");
            }
            if (r.getCitySequence().contains("C")) {
                totalDeliveredC += r.getDeliveredForCity("C");
            }
        }
        assertEquals(120, totalDeliveredB, "Total delivered to B should fulfill its demand");
        assertEquals(80, totalDeliveredC, "Total delivered to C should fulfill its demand");
    }

    @Test
    public void testNoFeasibleRoute() {
        // Scenario: The maximum route duration is too short to complete any round trip.
        String depot = "A";
        List<String> cities = Arrays.asList("A", "B");
        List<EdgeData> edges = Arrays.asList(
            new EdgeData("A", "B", 5.0, 20),
            new EdgeData("B", "A", 5.0, 20)
        );

        Graph graph = createGraph(depot, cities, edges);
        Map<String, Integer> demand = new HashMap<>();
        demand.put("B", 50);

        int vehicleCapacity = 100;
        int maxDuration = 30; // Not enough time for the round trip (requires 40 time units)
        double costMultiplier = 1.0;

        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            planner.planRoutes(graph, demand, depot, vehicleCapacity, maxDuration, costMultiplier);
        });
        String expectedMessage = "No feasible route";
        assertTrue(exception.getMessage().contains(expectedMessage), "Should indicate that no feasible route exists under the duration constraint");
    }

    @Test
    public void testDepotNoOutgoingEdges() {
        // Scenario: Depot has no outgoing edges.
        String depot = "A";
        List<String> cities = Arrays.asList("A", "B");
        // Only an edge from B to A is provided.
        List<EdgeData> edges = Arrays.asList(
            new EdgeData("B", "A", 5.0, 10)
        );

        Graph graph = createGraph(depot, cities, edges);
        Map<String, Integer> demand = new HashMap<>();
        demand.put("B", 50);

        int vehicleCapacity = 100;
        int maxDuration = 30;
        double costMultiplier = 1.0;

        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            planner.planRoutes(graph, demand, depot, vehicleCapacity, maxDuration, costMultiplier);
        });
        String expectedMessage = "Depot has no outgoing edges";
        assertTrue(exception.getMessage().contains(expectedMessage), "Should indicate an error when the depot has no outgoing routes");
    }

    @Test
    public void testZeroDemandCity() {
        // Scenario: A city with zero demand should not be included in any computed route.
        String depot = "A";
        List<String> cities = Arrays.asList("A", "B", "C");
        List<EdgeData> edges = Arrays.asList(
            new EdgeData("A", "B", 3.0, 5),
            new EdgeData("B", "A", 3.0, 5),
            new EdgeData("A", "C", 4.0, 7),
            new EdgeData("C", "A", 4.0, 7)
        );

        Graph graph = createGraph(depot, cities, edges);
        Map<String, Integer> demand = new HashMap<>();
        demand.put("B", 50);
        demand.put("C", 0);

        int vehicleCapacity = 100;
        int maxDuration = 30;
        double costMultiplier = 1.0;

        List<Route> routes = planner.planRoutes(graph, demand, depot, vehicleCapacity, maxDuration, costMultiplier);

        assertNotNull(routes, "Routes list should not be null");
        for (Route r : routes) {
            assertFalse(r.getCitySequence().contains("C"), "Cities with zero demand should not appear in any route");
        }
    }
}