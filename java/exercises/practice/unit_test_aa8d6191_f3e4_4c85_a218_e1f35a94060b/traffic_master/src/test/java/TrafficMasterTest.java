package traffic_master;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;

public class TrafficMasterTest {

    // Helper method to create a simple city graph with 2 intersections and 1 road.
    private Graph createSimpleGraph() {
        Graph graph = new Graph();
        graph.addIntersection(1);
        graph.addIntersection(2);
        // Add a road from intersection 1 to 2 with capacity 10 and travel time 5.0 seconds.
        graph.addRoad(1, 2, 10, 5.0);
        return graph;
    }

    // Helper method to create a list with one vehicle request.
    private List<VehicleRequest> createVehicleRequestsSimple() {
        List<VehicleRequest> requests = new ArrayList<>();
        // One vehicle request from intersection 1 to 2 arriving at time 0.0.
        requests.add(new VehicleRequest(1, 2, 0.0));
        return requests;
    }

    @Test
    public void testEmptySimulation() {
        // Test simulation when the city graph is empty and there are no vehicle requests.
        Graph graph = new Graph();
        List<VehicleRequest> requests = new ArrayList<>();
        SimulationParameters params = new SimulationParameters(60.0, 15.0, 30.0, 180.0);
        
        TrafficMaster simulation = new TrafficMaster(graph, requests, params);
        SimulationResult result = simulation.runSimulation();

        // Validate result is not null.
        assertNotNull(result, "Result of simulation should not be null");
        // Throughput should be zero since no vehicles are present.
        assertEquals(0, result.getThroughput(), "Throughput should be 0 for empty simulation");
        // Average travel time should be 0 since no vehicle reaches destination.
        assertEquals(0.0, result.getAverageTravelTime(), "Average travel time should be 0 for empty simulation");
    }

    @Test
    public void testSingleVehicleJourney() {
        // Test simulation on a simple graph with one vehicle request.
        Graph graph = createSimpleGraph();
        List<VehicleRequest> requests = createVehicleRequestsSimple();
        SimulationParameters params = new SimulationParameters(60.0, 15.0, 30.0, 180.0);
        
        TrafficMaster simulation = new TrafficMaster(graph, requests, params);
        SimulationResult result = simulation.runSimulation();

        // Validate that simulation result is not null.
        assertNotNull(result, "Result should not be null");
        // Throughput should be 1 since one vehicle is simulated.
        assertEquals(1, result.getThroughput(), "Throughput should be 1 for one vehicle request");

        List<VehicleLog> logs = result.getVehicleLogs();
        assertEquals(1, logs.size(), "There should be exactly one vehicle log");

        VehicleLog log = logs.get(0);
        // The travel time (arrival at destination - departure from source) should be at least equal to the road travel time.
        double travelTime = log.getArrivalTimeDestination() - log.getDepartureTimeSource();
        assertTrue(travelTime >= 5.0, "Travel time should be at least the defined road travel time");
    }

    @Test
    public void testMultipleVehiclesAndQueueing() {
        // Construct a graph with limited road capacity to force queueing at the intersection.
        Graph graph = new Graph();
        graph.addIntersection(1);
        graph.addIntersection(2);
        // Road from intersection 1 to 2 with capacity 1 and travel time 3.0 seconds.
        graph.addRoad(1, 2, 1, 3.0);

        // Create 5 vehicle requests arriving at consecutive time units.
        List<VehicleRequest> requests = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            requests.add(new VehicleRequest(1, 2, (double) i));
        }

        SimulationParameters params = new SimulationParameters(60.0, 15.0, 30.0, 180.0);
        TrafficMaster simulation = new TrafficMaster(graph, requests, params);
        SimulationResult result = simulation.runSimulation();

        // All vehicles should eventually reach their destination.
        assertNotNull(result, "Simulation result should not be null");
        assertEquals(5, result.getThroughput(), "Throughput should be 5 for five vehicle requests");
        // Since the road capacity is low, a queue must have formed.
        assertTrue(result.getMaximumQueueLength() >= 1, "Maximum queue length should be at least 1 due to limited capacity");
    }

    @Test
    public void testAdaptiveTrafficControlPolicyAdjustment() {
        // Create a graph with three intersections and two roads forming a path.
        Graph graph = new Graph();
        graph.addIntersection(1);
        graph.addIntersection(2);
        graph.addIntersection(3);
        // Road from 1 to 2 with capacity 5 and travel time 4.0 seconds.
        graph.addRoad(1, 2, 5, 4.0);
        // Road from 2 to 3 with capacity 5 and travel time 6.0 seconds.
        graph.addRoad(2, 3, 5, 6.0);

        // Create 10 vehicle requests with staggered arrival times along the path.
        List<VehicleRequest> requests = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            requests.add(new VehicleRequest(1, 3, i * 2.0));
        }

        SimulationParameters params = new SimulationParameters(120.0, 30.0, 30.0, 180.0);
        TrafficMaster simulation = new TrafficMaster(graph, requests, params);
        SimulationResult result = simulation.runSimulation();

        // Validate final traffic policies are set and within the allowed cycle length limits.
        Map<Integer, TrafficLightPolicy> finalPolicies = result.getFinalTrafficPolicies();
        assertNotNull(finalPolicies, "Traffic policies should not be null");

        for (TrafficLightPolicy policy : finalPolicies.values()) {
            double cycleLength = policy.getCycleLength();
            assertTrue(cycleLength >= params.getMinCycleLength() && cycleLength <= params.getMaxCycleLength(),
                       "Cycle length should be within the allowed limits");
            double totalGreen = policy.getGreenDurations()
                                      .values()
                                      .stream()
                                      .mapToDouble(Double::doubleValue)
                                      .sum();
            assertEquals(cycleLength, totalGreen, 0.001, "Sum of green durations should equal the cycle length");
        }

        // Validate performance metrics.
        PerformanceMetrics metrics = result.getPerformanceMetrics();
        assertNotNull(metrics, "Performance metrics should not be null");
        assertTrue(metrics.getAverageTravelTime() > 0, "Average travel time should be positive");
        assertTrue(metrics.getTotalJerk() >= 0, "Total jerk should be non-negative");
    }

    @Test
    public void testRealWorldScaleSimulation() {
        // Create a larger graph with 50 intersections.
        Graph graph = new Graph();
        int numIntersections = 50;
        for (int i = 1; i <= numIntersections; i++) {
            graph.addIntersection(i);
        }
        // Connect intersections with two-way roads.
        Random rand = new Random(42);
        for (int i = 1; i < numIntersections; i++) {
            int j = i + 1;
            int capacity = rand.nextInt(5) + 1; // capacity between 1 and 5
            double travelTime = 2.0 + rand.nextDouble() * 6.0; // travel time between 2.0 and 8.0 seconds
            graph.addRoad(i, j, capacity, travelTime);
            graph.addRoad(j, i, capacity, travelTime + 0.5); // simulate two-way road with slight delay
        }

        // Create 100 vehicle requests with random start and destination.
        List<VehicleRequest> requests = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            int start = rand.nextInt(numIntersections) + 1;
            int end;
            do {
                end = rand.nextInt(numIntersections) + 1;
            } while (end == start);
            double arrivalTime = rand.nextDouble() * 120; // arrival time within first 2 minutes
            requests.add(new VehicleRequest(start, end, arrivalTime));
        }

        SimulationParameters params = new SimulationParameters(300.0, 30.0, 30.0, 180.0);
        TrafficMaster simulation = new TrafficMaster(graph, requests, params);
        SimulationResult result = simulation.runSimulation();

        // Validate simulation results.
        assertNotNull(result, "Result should not be null");
        PerformanceMetrics metrics = result.getPerformanceMetrics();
        assertNotNull(metrics, "Performance metrics should not be null");

        // All vehicle requests are expected to eventually reach their destinations.
        assertEquals(100, result.getThroughput(), "Throughput should equal the number of vehicle requests (100)");
        assertTrue(metrics.getAverageTravelTime() > 0, "Average travel time should be positive");

        // Validate road utilization is within the range [0, 1].
        Map<String, Double> roadUtilization = metrics.getRoadUtilization();
        assertNotNull(roadUtilization, "Road utilization metrics should not be null");
        for (Double utilization : roadUtilization.values()) {
            assertTrue(utilization >= 0 && utilization <= 1, "Each road utilization should be between 0 and 1");
        }
    }
}