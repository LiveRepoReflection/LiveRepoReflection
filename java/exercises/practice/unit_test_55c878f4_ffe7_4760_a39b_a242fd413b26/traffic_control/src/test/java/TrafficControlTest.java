package traffic_control;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class TrafficControlTest {
    private TrafficControl trafficControl;

    @Before
    public void setUp() {
        trafficControl = new TrafficControl();
    }

    @Test
    public void testBasicRouting() {
        // Add intersections
        trafficControl.addIntersection(1);
        trafficControl.addIntersection(2);
        trafficControl.addIntersection(3);
        trafficControl.addIntersection(4);
        
        // Add roads with capacities
        trafficControl.addRoad(1, 2, 15);
        trafficControl.addRoad(2, 3, 15);
        trafficControl.addRoad(3, 4, 15);
        
        // Add traffic demand from intersection 1 to 4 with demand 10
        trafficControl.addTrafficDemand(1, 4, 10);
        
        // Attempt routing
        boolean success = trafficControl.routeTraffic();
        assertTrue("Basic routing should succeed", success);
        
        // Verify congestion metric is computed properly (non-negative)
        int congestion = trafficControl.getCongestionMetric();
        assertTrue("Congestion metric should be non-negative", congestion >= 0);
    }

    @Test
    public void testDynamicUpdateCapacity() {
        // Create network with one road and a traffic demand
        trafficControl.addIntersection(1);
        trafficControl.addIntersection(2);
        trafficControl.addRoad(1, 2, 10);
        trafficControl.addTrafficDemand(1, 2, 8);
        
        boolean success = trafficControl.routeTraffic();
        assertTrue("Initial routing should succeed", success);
        
        // Update road capacity to a lower value making the demand exceed capacity
        trafficControl.updateRoadCapacity(1, 2, 5);
        success = trafficControl.routeTraffic();
        assertFalse("Routing should fail when capacity is below demand", success);
        
        // Update traffic demand to match new capacity and re-route
        trafficControl.updateTrafficDemand(1, 2, 5);
        success = trafficControl.routeTraffic();
        assertTrue("Routing should succeed after aligning demand with capacity", success);
    }

    @Test
    public void testAddAndRemoveRoad() {
        // Setup a network with two alternative routes between 1 and 5
        for (int i = 1; i <= 5; i++) {
            trafficControl.addIntersection(i);
        }
        // Route 1: 1 -> 2 -> 5
        trafficControl.addRoad(1, 2, 10);
        trafficControl.addRoad(2, 5, 10);
        
        // Route 2: 1 -> 3 -> 4 -> 5
        trafficControl.addRoad(1, 3, 10);
        trafficControl.addRoad(3, 4, 10);
        trafficControl.addRoad(4, 5, 10);
        
        // Add traffic demand from 1 to 5 (demand 10)
        trafficControl.addTrafficDemand(1, 5, 10);
        
        // Initial routing should succeed
        boolean success = trafficControl.routeTraffic();
        assertTrue("Routing should succeed with both routes available", success);
        int congestionInitial = trafficControl.getCongestionMetric();
        
        // Remove route 1 completely to force usage of route 2
        trafficControl.removeRoad(1, 2);
        trafficControl.removeRoad(2, 5);
        success = trafficControl.routeTraffic();
        assertTrue("Routing should succeed with only one route available", success);
        int congestionAfterRemoval = trafficControl.getCongestionMetric();
        
        // Expect congestion to increase as fewer routes are available
        assertTrue("Congestion should increase after route removal", congestionAfterRemoval > congestionInitial);
    }

    @Test
    public void testFaultTolerance() {
        // Build network with a primary route and a backup route for fault tolerance
        for (int i = 1; i <= 6; i++) {
            trafficControl.addIntersection(i);
        }
        // Primary route: 1 -> 2 -> 3 -> 6
        trafficControl.addRoad(1, 2, 10);
        trafficControl.addRoad(2, 3, 10);
        trafficControl.addRoad(3, 6, 10);
        
        // Backup route: 1 -> 4 -> 5 -> 6
        trafficControl.addRoad(1, 4, 8);
        trafficControl.addRoad(4, 5, 8);
        trafficControl.addRoad(5, 6, 8);
        
        // Add traffic demand from 1 to 6 of 8 vehicles
        trafficControl.addTrafficDemand(1, 6, 8);
        
        // Initial routing should succeed using available routes
        boolean success = trafficControl.routeTraffic();
        assertTrue("Initial routing should succeed", success);
        
        // Simulate fault by removing a key road from the primary route (e.g., 2 -> 3)
        trafficControl.removeRoad(2, 3);
        
        // Re-route traffic, expecting backup route to be used
        success = trafficControl.routeTraffic();
        assertTrue("Routing should succeed using backup route after fault", success);
        
        int congestion = trafficControl.getCongestionMetric();
        assertTrue("Congestion metric should be non-negative", congestion >= 0);
    }

    @Test
    public void testMultipleTrafficDemands() {
        // Build a network with several intersections and overlapping demands
        for (int i = 1; i <= 7; i++) {
            trafficControl.addIntersection(i);
        }
        // Define roads in the network
        trafficControl.addRoad(1, 2, 15);
        trafficControl.addRoad(2, 3, 15);
        trafficControl.addRoad(3, 7, 15);
        trafficControl.addRoad(1, 4, 10);
        trafficControl.addRoad(4, 5, 10);
        trafficControl.addRoad(5, 7, 10);
        trafficControl.addRoad(1, 6, 5);
        trafficControl.addRoad(6, 7, 5);
        
        // Add multiple traffic demands
        trafficControl.addTrafficDemand(1, 7, 10);
        trafficControl.addTrafficDemand(1, 3, 5);
        trafficControl.addTrafficDemand(4, 7, 7);
        trafficControl.addTrafficDemand(6, 7, 4);
        
        boolean success = trafficControl.routeTraffic();
        assertTrue("Routing should succeed with multiple traffic demands", success);
        
        int congestion = trafficControl.getCongestionMetric();
        assertTrue("Congestion metric should be non-negative", congestion >= 0);
    }
}