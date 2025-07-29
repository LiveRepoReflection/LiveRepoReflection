import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;

public class TrafficOptTest {

    private TrafficOptimizer optimizer;

    @BeforeEach
    public void setUp() {
        // TrafficOptimizer is assumed to be the main class that provides the optimize method.
        optimizer = new TrafficOptimizer();
    }

    @Test
    public void testOptimalConfigurationFound() {
        // Setup a small connected graph with three intersections.
        List<Integer> intersections = new ArrayList<>();
        intersections.add(1);
        intersections.add(2);
        intersections.add(3);

        List<Road> roads = new ArrayList<>();
        // Construct roads: Road(source, destination, capacity, travelTime)
        roads.add(new Road(1, 2, 100, 5));
        roads.add(new Road(2, 3, 100, 5));
        roads.add(new Road(1, 3, 50, 15));

        // Setup an OD pair with a positive demand.
        List<OdPair> odPairs = new ArrayList<>();
        odPairs.add(new OdPair(1, 3, 80));

        // Define traffic light parameters.
        int minCycleTime = 30;
        int maxCycleTime = 120;
        int minGreenTime = 5;

        // Invoke the optimizer.
        OptimizationResult result = optimizer.optimize(intersections, roads, odPairs, minCycleTime, maxCycleTime, minGreenTime);

        // Validate that an optimization result was returned.
        Assertions.assertNotNull(result, "The optimization result should not be null.");
        // Validate that the average travel time is computed as a finite value.
        Assertions.assertTrue(result.getAverageTravelTime() < Double.MAX_VALUE, "The average travel time should be finite.");
        // Validate that the cycle time is within the specified bounds.
        int cycleTime = result.getCycleTime();
        Assertions.assertTrue(cycleTime >= minCycleTime && cycleTime <= maxCycleTime, "Cycle time must be within the specified range.");

        // Validate that each green time in the schedule meets the minimum green time requirement.
        Map<Integer, Map<Integer, Integer>> schedule = result.getSchedule();
        for (Map<Integer, Integer> phaseMap : schedule.values()) {
            for (Integer greenTime : phaseMap.values()) {
                Assertions.assertTrue(greenTime >= minGreenTime, "Each green time value must be at least the minimum green time.");
            }
        }
    }

    @Test
    public void testDisconnectedGraph() {
        // Setup a graph with a disconnected intersection.
        List<Integer> intersections = new ArrayList<>();
        intersections.add(1);
        intersections.add(2);
        intersections.add(3);

        List<Road> roads = new ArrayList<>();
        // Only one road connects node 1 and node 2; node 3 is disconnected.
        roads.add(new Road(1, 2, 100, 5));

        // Create an OD pair that involves the disconnected intersection.
        List<OdPair> odPairs = new ArrayList<>();
        odPairs.add(new OdPair(1, 3, 50));

        int minCycleTime = 30;
        int maxCycleTime = 120;
        int minGreenTime = 5;

        OptimizationResult result = optimizer.optimize(intersections, roads, odPairs, minCycleTime, maxCycleTime, minGreenTime);

        // Expect the optimizer to return a failure outcome.
        Assertions.assertEquals(Double.MAX_VALUE, result.getAverageTravelTime(), "Average travel time should be Double.MAX_VALUE for unreachable OD pairs.");
        Assertions.assertTrue(result.getErrorMessage() != null && !result.getErrorMessage().isEmpty(), "An appropriate error message should be returned for a disconnected graph.");
    }

    @Test
    public void testZeroDemand() {
        // Setup a simple graph with two intersections connected by a road.
        List<Integer> intersections = new ArrayList<>();
        intersections.add(1);
        intersections.add(2);

        List<Road> roads = new ArrayList<>();
        roads.add(new Road(1, 2, 100, 5));

        // Create an OD pair with zero demand.
        List<OdPair> odPairs = new ArrayList<>();
        odPairs.add(new OdPair(1, 2, 0));

        int minCycleTime = 30;
        int maxCycleTime = 120;
        int minGreenTime = 5;

        OptimizationResult result = optimizer.optimize(intersections, roads, odPairs, minCycleTime, maxCycleTime, minGreenTime);

        // With zero demand, the average travel time is expected to be zero.
        Assertions.assertEquals(0.0, result.getAverageTravelTime(), "Average travel time should be zero when there is no traffic demand.");
    }

    @Test
    public void testHighDemandAndCongestion() {
        // Setup a more complex graph to simulate congestion.
        List<Integer> intersections = new ArrayList<>();
        intersections.add(1);
        intersections.add(2);
        intersections.add(3);
        intersections.add(4);

        List<Road> roads = new ArrayList<>();
        roads.add(new Road(1, 2, 50, 10));
        roads.add(new Road(2, 3, 50, 10));
        roads.add(new Road(3, 4, 50, 10));
        roads.add(new Road(1, 3, 30, 20));
        roads.add(new Road(2, 4, 30, 20));

        // Multiple OD pairs with high traffic demand.
        List<OdPair> odPairs = new ArrayList<>();
        odPairs.add(new OdPair(1, 4, 120));
        odPairs.add(new OdPair(1, 3, 80));
        odPairs.add(new OdPair(2, 4, 100));

        int minCycleTime = 40;
        int maxCycleTime = 100;
        int minGreenTime = 10;

        OptimizationResult result = optimizer.optimize(intersections, roads, odPairs, minCycleTime, maxCycleTime, minGreenTime);

        // Check that the result indicates a congested yet feasible scenario.
        Assertions.assertTrue(result.getAverageTravelTime() > 0 && result.getAverageTravelTime() < Double.MAX_VALUE, "Average travel time must be a positive finite value for congested scenarios.");
        int cycleTime = result.getCycleTime();
        Assertions.assertTrue(cycleTime >= minCycleTime && cycleTime <= maxCycleTime, "Cycle time must be within the specified limits.");

        Map<Integer, Map<Integer, Integer>> schedule = result.getSchedule();
        for (Map<Integer, Integer> phaseMap : schedule.values()) {
            for (Integer greenTime : phaseMap.values()) {
                Assertions.assertTrue(greenTime >= minGreenTime, "Each green time must satisfy the minimum green time constraint.");
            }
        }
    }
}