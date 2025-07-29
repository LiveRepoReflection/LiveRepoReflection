import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

class RouteOptimizerTest {

    private RouteOptimizer optimizer;

    @BeforeEach
    void setUp() {
        optimizer = new RouteOptimizer();
    }

    @Test
    void testSimpleRoutePlanning() {
        // Create a simple graph with three locations: depot, A, and B
        DeliveryLocation depot = new DeliveryLocation("D", 0.0, 0.0, 0, 0, 24);
        DeliveryLocation locA = new DeliveryLocation("A", 1.0, 1.0, 10, 8, 12);
        DeliveryLocation locB = new DeliveryLocation("B", 2.0, 2.0, 15, 9, 13);

        Graph graph = new Graph();
        graph.addLocation(depot);
        graph.addLocation(locA);
        graph.addLocation(locB);

        // Add road segments between locations (bidirectional connections)
        graph.addRoadSegment(new RoadSegment("D", "A", 5));
        graph.addRoadSegment(new RoadSegment("A", "B", 7));
        graph.addRoadSegment(new RoadSegment("D", "B", 10));
        graph.addRoadSegment(new RoadSegment("B", "A", 7));
        graph.addRoadSegment(new RoadSegment("A", "D", 5));
        graph.addRoadSegment(new RoadSegment("B", "D", 10));

        // Create a vehicle with sufficient capacity for both deliveries
        Vehicle vehicle1 = new Vehicle("V1", 20, 1.0);
        List<Vehicle> vehicles = new ArrayList<>();
        vehicles.add(vehicle1);

        // Execute route planning
        RoutePlan plan = optimizer.planRoutes(depot, vehicles, graph);

        // Validate that total cost is non-negative
        assertTrue(plan.getTotalCost() >= 0, "Total cost should be non-negative.");

        // Verify that at least one route is returned for the available vehicle(s)
        assertNotNull(plan.getRoutes(), "Routes should not be null.");
        assertTrue(plan.getRoutes().size() > 0, "At least one route should be planned.");

        // Ensure that the unserved locations list is neither null nor missing
        assertNotNull(plan.getUnservedLocations(), "Unserved locations list should not be null.");
    }

    @Test
    void testDeliveryTimeWindowConstraints() {
        // Create a scenario with a tight time window that forces the planner to decide between waiting or marking as unserved.
        DeliveryLocation depot = new DeliveryLocation("D", 0.0, 0.0, 0, 0, 24);
        DeliveryLocation locTight = new DeliveryLocation("T", 1.0, 1.0, 5, 9, 9); // narrow time window at 9

        Graph graph = new Graph();
        graph.addLocation(depot);
        graph.addLocation(locTight);
        graph.addRoadSegment(new RoadSegment("D", "T", 3));
        graph.addRoadSegment(new RoadSegment("T", "D", 3));

        Vehicle vehicle = new Vehicle("V1", 10, 1.0);
        List<Vehicle> vehicles = Collections.singletonList(vehicle);

        RoutePlan plan = optimizer.planRoutes(depot, vehicles, graph);

        // Check if the delivery location was visited in a route. If yes, ensure arrival time respects the time window.
        // Otherwise, the location should appear in the unserved locations list.
        boolean served = false;
        for (Route route : plan.getRoutes()) {
            if (route.containsLocation("T")) {
                served = true;
                int arrivalTime = route.getArrivalTimeAt("T");
                assertTrue(arrivalTime >= 9, "Arrival time should respect the start of the time window.");
            }
        }
        if (!served) {
            assertTrue(plan.getUnservedLocations().contains("T"),
                "Location T should be unserved if its time window constraints cannot be met.");
        }
    }

    @Test
    void testVehicleCapacityConstraints() {
        // Test a scenario where the delivery demand exceeds the vehicle's capacity.
        DeliveryLocation depot = new DeliveryLocation("D", 0.0, 0.0, 0, 0, 24);
        DeliveryLocation locHeavy = new DeliveryLocation("H", 1.0, 1.0, 50, 8, 18); // demand is 50
        Graph graph = new Graph();
        graph.addLocation(depot);
        graph.addLocation(locHeavy);
        graph.addRoadSegment(new RoadSegment("D", "H", 10));
        graph.addRoadSegment(new RoadSegment("H", "D", 10));

        // Vehicle capacity is insufficient for locHeavy's demand
        Vehicle vehicle = new Vehicle("V1", 20, 1.0);
        List<Vehicle> vehicles = Collections.singletonList(vehicle);

        RoutePlan plan = optimizer.planRoutes(depot, vehicles, graph);

        // The heavy demand location should be marked as unserved.
        assertTrue(plan.getUnservedLocations().contains("H"),
            "Location H must be unserved due to insufficient vehicle capacity.");
    }

    @Test
    void testDisconnectedGraphHandling() {
        // Build a graph where one location is isolated from the depot.
        DeliveryLocation depot = new DeliveryLocation("D", 0.0, 0.0, 0, 0, 24);
        DeliveryLocation locIsolated = new DeliveryLocation("I", 10.0, 10.0, 10, 8, 18);
        Graph graph = new Graph();
        graph.addLocation(depot);
        graph.addLocation(locIsolated);
        // No road segments connect depot and isolated location

        Vehicle vehicle = new Vehicle("V1", 30, 1.0);
        List<Vehicle> vehicles = new ArrayList<>();
        vehicles.add(vehicle);

        RoutePlan plan = optimizer.planRoutes(depot, vehicles, graph);

        // The isolated location must be reported as unserved.
        assertTrue(plan.getUnservedLocations().contains("I"),
            "Disconnected location should be marked as unserved.");
    }

    @Test
    void testDynamicUpdatesAnnotation() {
        // Although dynamic updates are not fully implemented, simulate the addition of a new road segment.
        DeliveryLocation depot = new DeliveryLocation("D", 0.0, 0.0, 0, 0, 24);
        DeliveryLocation locA = new DeliveryLocation("A", 1.0, 1.0, 10, 8, 15);
        Graph graph = new Graph();
        graph.addLocation(depot);
        graph.addLocation(locA);
        graph.addRoadSegment(new RoadSegment("D", "A", 5));
        graph.addRoadSegment(new RoadSegment("A", "D", 5));

        Vehicle vehicle = new Vehicle("V1", 15, 1.0);
        List<Vehicle> vehicles = Collections.singletonList(vehicle);

        // Simulate a dynamic update by adding an alternative, lower-cost edge.
        graph.addRoadSegment(new RoadSegment("D", "A", 3));

        RoutePlan plan = optimizer.planRoutes(depot, vehicles, graph);

        // Verify that the plan remains valid after a dynamic update.
        assertNotNull(plan.getRoutes(), "Routes should not be null after dynamic updates.");
        assertTrue(plan.getRoutes().size() > 0, "At least one route should be planned after a dynamic update.");
    }
}