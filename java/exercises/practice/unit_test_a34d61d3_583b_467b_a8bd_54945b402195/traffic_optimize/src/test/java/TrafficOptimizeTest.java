package traffic_optimize;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

public class TrafficOptimizeTest {

    private TrafficNetwork network;

    @BeforeEach
    public void setUp() {
        network = new TrafficNetwork();
        // Add intersections 0 to 4
        for (int i = 0; i < 5; i++) {
            network.addIntersection(i);
        }
        // Add roads with parameters: from, to, baseTravelTime, capacity
        network.addRoad(0, 1, 5.0, 100);
        network.addRoad(1, 2, 5.0, 100);
        network.addRoad(0, 2, 15.0, 100);
        network.addRoad(2, 3, 10.0, 50);
        network.addRoad(1, 3, 20.0, 50);
        network.addRoad(3, 4, 5.0, 100);
        network.addRoad(2, 4, 25.0, 80);
    }

    @Test
    public void testShortestPathDirect() {
        // Configure traffic flows so that path 0->1->2 is preferable.
        network.updateTrafficFlow(0, 1, 20);
        network.updateTrafficFlow(1, 2, 20);
        network.updateTrafficFlow(0, 2, 0);

        List<Integer> path = network.shortestPath(0, 2);
        // Expected path: [0, 1, 2]
        assertNotNull(path, "Path should not be null");
        assertEquals(3, path.size(), "Path length should be 3");
        assertEquals(0, path.get(0), "Path should start with 0");
        assertEquals(1, path.get(1), "Path should pass through 1");
        assertEquals(2, path.get(2), "Path should end with 2");
    }

    @Test
    public void testShortestPathAlternative() {
        // Increase traffic on 0->1 so that direct edge 0->2 becomes faster.
        network.updateTrafficFlow(0, 1, 100);
        network.updateTrafficFlow(1, 2, 20);
        network.updateTrafficFlow(0, 2, 0);

        List<Integer> path = network.shortestPath(0, 2);
        // Expected path: [0, 2]
        assertNotNull(path, "Path should not be null");
        assertEquals(2, path.size(), "Path length should be 2");
        assertEquals(0, path.get(0), "Path should start with 0");
        assertEquals(2, path.get(1), "Path should end with 2");
    }
    
    @Test
    public void testTrafficReroutingRecommendationImprovement() {
        // Configure a scenario from 0 to 4 with varying traffic flows.
        network.updateTrafficFlow(0, 1, 50);
        network.updateTrafficFlow(1, 2, 40);
        network.updateTrafficFlow(0, 2, 20);
        network.updateTrafficFlow(2, 3, 30);
        network.updateTrafficFlow(1, 3, 30);
        network.updateTrafficFlow(3, 4, 60);
        network.updateTrafficFlow(2, 4, 40);

        double beforeTotalTime = network.getTotalNetworkTravelTime();

        // Request a rerouting recommendation for at least 50% of vehicles between 0 and 4.
        TrafficReroutingResult result = network.rerouteTraffic(0, 4, 50.0);
        double afterTotalTime = result.getAfterTotalTime();

        // Assert that the overall travel time is reduced after rerouting.
        assertTrue(afterTotalTime < beforeTotalTime, "Total travel time should decrease after rerouting");
        // Assert that the rerouted flow meets the threshold requirement.
        assertTrue(result.getReroutedFlow() >= 0.5 * result.getOriginalFlow(), "Rerouted flow should be at least 50% of original flow");
    }

    @Test
    public void testEdgeCaseNoTraffic() {
        // Set all road traffic flows to zero so that travel times equal base travel times.
        network.updateTrafficFlow(0, 1, 0);
        network.updateTrafficFlow(1, 2, 0);
        network.updateTrafficFlow(0, 2, 0);

        List<Integer> path = network.shortestPath(0, 2);
        double pathTravelTime = network.getPathTravelTime(path);
        // For path 0->1->2, expected travel time is 5.0 + 5.0 = 10.0.
        assertEquals(10.0, pathTravelTime, 0.001, "Travel time should equal the sum of base travel times");
    }

    @Test
    public void testDynamicUpdate() {
        // Test that updating traffic flows dynamically changes the computed shortest path.
        network.updateTrafficFlow(0, 1, 10);
        network.updateTrafficFlow(1, 2, 10);

        List<Integer> initialPath = network.shortestPath(0, 2);
        double initialTime = network.getPathTravelTime(initialPath);

        // Increase traffic on edge 0->1 significantly.
        network.updateTrafficFlow(0, 1, 90);
        List<Integer> newPath = network.shortestPath(0, 2);
        double newTime = network.getPathTravelTime(newPath);

        // The travel time after update should be greater if the same route is taken,
        // or the algorithm may choose an alternate route with improved travel time.
        assertTrue(newTime >= initialTime, "Updated path travel time should reflect higher congestion");
        // If the path changes, ensure that the selected route is valid.
        if (!initialPath.equals(newPath)) {
            double alternateTime = network.getPathTravelTime(newPath);
            assertTrue(alternateTime <= newTime, "Alternate route should have travel time consistent with computed value");
        }
    }
}