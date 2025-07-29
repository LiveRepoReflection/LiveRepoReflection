import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Test;

public class OptimalRoutingTest {

    private static final double DELTA = 1e-6;

    @Test
    public void testSingleDeliveryNoWait() {
        int numLocations = 2;
        
        List<int[]> roads = new ArrayList<>();
        // Road from depot (0) to delivery (1) with travelTime=10 and tollCost=5.
        roads.add(new int[]{0, 1, 10, 5});
        
        List<Integer> deliveryDestinations = new ArrayList<>();
        deliveryDestinations.add(1);
        
        Map<Integer, int[]> deliveryWindows = new HashMap<>();
        // Wide window so no waiting required.
        deliveryWindows.put(1, new int[]{0, 1440});
        
        double timeWeight = 1.0;
        double tollWeight = 1.0;
        
        // Expected cost = 10*1 + 5*1 = 15.
        double expectedCost = 15;
        
        double result = OptimalRouting.findOptimalRouteCost(numLocations, roads, deliveryDestinations, deliveryWindows, timeWeight, tollWeight);
        assertEquals(expectedCost, result, DELTA);
    }

    @Test
    public void testWaitScenario() {
        int numLocations = 2;
        
        List<int[]> roads = new ArrayList<>();
        // Road from depot (0) to delivery (1) with travelTime=5 and tollCost=2.
        roads.add(new int[]{0, 1, 5, 2});
        
        List<Integer> deliveryDestinations = new ArrayList<>();
        deliveryDestinations.add(1);
        
        Map<Integer, int[]> deliveryWindows = new HashMap<>();
        // Delivery window requires waiting since start time = 10.
        deliveryWindows.put(1, new int[]{10, 20});
        
        double timeWeight = 1.0;
        double tollWeight = 1.0;
        
        // Even though vehicle arrives at 5, it must wait until 10, but waiting is free.
        // Cost remains based solely on road travel: 5 + 2 = 7.
        double expectedCost = 7;
        
        double result = OptimalRouting.findOptimalRouteCost(numLocations, roads, deliveryDestinations, deliveryWindows, timeWeight, tollWeight);
        assertEquals(expectedCost, result, DELTA);
    }
    
    @Test
    public void testUnreachableDelivery() {
        int numLocations = 2;
        
        List<int[]> roads = new ArrayList<>();
        // No road from 0 to 1.
        
        List<Integer> deliveryDestinations = new ArrayList<>();
        deliveryDestinations.add(1);
        
        Map<Integer, int[]> deliveryWindows = new HashMap<>();
        deliveryWindows.put(1, new int[]{0, 1440});
        
        double timeWeight = 1.0;
        double tollWeight = 1.0;
        
        double result = OptimalRouting.findOptimalRouteCost(numLocations, roads, deliveryDestinations, deliveryWindows, timeWeight, tollWeight);
        assertEquals(Double.MAX_VALUE, result, DELTA);
    }
    
    @Test
    public void testCycleGraphOptimalRoute() {
        int numLocations = 3;
        
        List<int[]> roads = new ArrayList<>();
        // Two possible routes:
        // Route 1: 0 -> 1 -> 2.
        roads.add(new int[]{0, 1, 5, 5});
        roads.add(new int[]{1, 2, 5, 5});
        
        // Route 2: 0 -> 2, 2 -> 1 (alternate ordering).
        roads.add(new int[]{0, 2, 12, 1});
        roads.add(new int[]{2, 1, 3, 10});
        
        List<Integer> deliveryDestinations = new ArrayList<>();
        deliveryDestinations.add(1);
        deliveryDestinations.add(2);
        
        Map<Integer, int[]> deliveryWindows = new HashMap<>();
        // Wide windows so timing is not an issue.
        deliveryWindows.put(1, new int[]{0, 1440});
        deliveryWindows.put(2, new int[]{0, 1440});
        
        double timeWeight = 1.0;
        double tollWeight = 1.0;
        
        // For Route 1: cost = (5+5) + (5+5) = 20.
        // For Route 2: cost = (12+1) + (3+10) = 26.
        double expectedCost = 20;
        
        double result = OptimalRouting.findOptimalRouteCost(numLocations, roads, deliveryDestinations, deliveryWindows, timeWeight, tollWeight);
        assertEquals(expectedCost, result, DELTA);
    }
    
    @Test
    public void testTightWindowImpossible() {
        int numLocations = 2;
        
        List<int[]> roads = new ArrayList<>();
        // Road from depot (0) to delivery (1) with travelTime=10 and tollCost=2.
        roads.add(new int[]{0, 1, 10, 2});
        
        List<Integer> deliveryDestinations = new ArrayList<>();
        deliveryDestinations.add(1);
        
        Map<Integer, int[]> deliveryWindows = new HashMap<>();
        // Tight window that cannot be met: arrival at 10 > end time of 5.
        deliveryWindows.put(1, new int[]{0, 5});
        
        double timeWeight = 1.0;
        double tollWeight = 1.0;
        
        double result = OptimalRouting.findOptimalRouteCost(numLocations, roads, deliveryDestinations, deliveryWindows, timeWeight, tollWeight);
        assertTrue(result == Double.MAX_VALUE);
    }
}