package route_planner;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class RoutePlannerTest {

    @Test
    public void testSingleUpdateAndQuery() {
        // Create a RoutePlanner with 5 nodes
        RoutePlanner rp = new RoutePlanner(5);
        // Add edges with their default traversal times
        rp.addEdge(0, 1, 1);
        rp.addEdge(1, 2, 2);
        rp.addEdge(2, 3, 3);
        rp.addEdge(3, 4, 4);

        // Update the edge 0 -> 1 with a new traversal time at timestamp 5
        rp.updateRoute(0, 1, 5, 2);

        // Query optimal route from 0 to 4 at a time after the update.
        // Expected route: 0 -> 1 -> 2 -> 3 -> 4, with updated weight on 0->1.
        int expected = 2 + 2 + 3 + 4; 
        int result = rp.getOptimalDeliveryRoute(0, 4, 10);
        assertEquals(expected, result);
    }

    @Test
    public void testNoPath() {
        // Create a RoutePlanner with 3 nodes
        RoutePlanner rp = new RoutePlanner(3);
        // Add directed edges
        rp.addEdge(0, 1, 5);
        rp.addEdge(1, 2, 10);
        // Update edges such that we have a valid path from 0 to 2.
        rp.updateRoute(0, 1, 1, 4);
        rp.updateRoute(1, 2, 1, 8);
        int result = rp.getOptimalDeliveryRoute(0, 2, 2);
        assertEquals(4 + 8, result);

        // Query from 2 to 0, where no path exists. Assume no path is indicated by -1.
        result = rp.getOptimalDeliveryRoute(2, 0, 2);
        assertEquals(-1, result);
    }

    @Test
    public void testMultipleUpdates() {
        // Create a RoutePlanner with 4 nodes
        RoutePlanner rp = new RoutePlanner(4);
        // Setup graph edges with default times
        rp.addEdge(0, 1, 10);
        rp.addEdge(1, 2, 10);
        rp.addEdge(0, 2, 25);
        rp.addEdge(2, 3, 5);
         
        // Apply updates at defined timestamps:
        rp.updateRoute(0, 1, 5, 2);
        rp.updateRoute(1, 2, 5, 3);
        rp.updateRoute(0, 2, 7, 4);

        // For query at time 6, the direct edge 0->2 is not yet updated.
        // Optimal path: 0->1 (2) + 1->2 (3) + 2->3 (5) = 10.
        int result = rp.getOptimalDeliveryRoute(0, 3, 6);
        assertEquals(10, result);

        // For query at time 8, the updated direct edge 0->2 becomes available.
        // Two candidate routes:
        // Route A: 0->1->2->3 = 2 + 3 + 5 = 10.
        // Route B: 0->2->3 = 4 + 5 = 9.
        // Optimal route is Route B.
        result = rp.getOptimalDeliveryRoute(0, 3, 8);
        assertEquals(9, result);
    }

    @Test
    public void testSelfLoopAndParallelEdges() {
        // Create a RoutePlanner with 3 nodes
        RoutePlanner rp = new RoutePlanner(3);
        // Add a self-loop and two parallel edges
        rp.addEdge(0, 0, 100);
        rp.addEdge(0, 1, 50);
        rp.addEdge(0, 1, 75);
        rp.addEdge(1, 2, 20);
        
        // Perform updates:
        rp.updateRoute(0, 0, 2, 10);
        rp.updateRoute(0, 1, 2, 40);
        // Simulate a later update that should be preferred for one of the parallel edges
        rp.updateRoute(0, 1, 4, 30);

        // For a query at time 5, the optimal use of the parallel edges should return the minimum possible route.
        // Expected path: 0 -> 1 using the updated edge with weight 30, then 1 -> 2 with 20 equals 50.
        int result = rp.getOptimalDeliveryRoute(0, 2, 5);
        assertEquals(50, result);
    }

    @Test
    public void testEdgeUpdateOrdering() {
        // Create a RoutePlanner with 3 nodes
        RoutePlanner rp = new RoutePlanner(3);
        rp.addEdge(0, 1, 10);
        rp.addEdge(1, 2, 10);

        // Apply multiple updates to the same edge at different timestamps.
        rp.updateRoute(0, 1, 3, 7);
        rp.updateRoute(0, 1, 5, 3);
         
        // Query at time 4 should reflect the update at timestamp 3.
        int result = rp.getOptimalDeliveryRoute(0, 1, 4);
        assertEquals(7, result);

        // Query at time 6 should reflect the update at timestamp 5.
        result = rp.getOptimalDeliveryRoute(0, 1, 6);
        assertEquals(3, result);
    }
}