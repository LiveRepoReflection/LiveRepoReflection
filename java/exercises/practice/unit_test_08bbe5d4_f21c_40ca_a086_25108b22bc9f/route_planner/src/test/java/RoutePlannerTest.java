import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class RoutePlannerTest {

    private RoutePlanner planner;

    @BeforeEach
    public void setUp() {
        planner = new RoutePlanner();
    }

    @Test
    public void testSimpleRoute() {
        // Construct a simple graph:
        // 1 -> 2, 2 -> 3
        // Road: (from, to, length, speedLimit)
        planner.addEdge(1, 2, 1000, 60);
        planner.addEdge(2, 3, 2000, 60);

        // For departure time 0, expected route is simply [1, 2, 3]
        List<Integer> route = planner.findFastestRoute(1, 3, 0);
        assertNotNull(route, "Route should not be null");
        assertEquals(Arrays.asList(1, 2, 3), route, "Route should be [1, 2, 3]");
    }

    @Test
    public void testNoRoute() {
        // Graph with disconnected nodes
        planner.addEdge(1, 2, 1000, 60);
        planner.addEdge(3, 4, 1500, 60);

        // No route exists between 1 and 4
        List<Integer> route = planner.findFastestRoute(1, 4, 0);
        assertNull(route, "Route should be null when no path exists");
    }

    @Test
    public void testSameStartAndEnd() {
        // When the start and end nodes are the same, 
        // the expected behavior is to return a route with a single node.
        List<Integer> route = planner.findFastestRoute(5, 5, 0);
        assertNotNull(route, "Route should not be null even if start equals end");
        assertEquals(1, route.size(), "Route should contain exactly one node");
        assertEquals(5, route.get(0), "Route should start and end with the same node");
    }

    @Test
    public void testTrafficUpdateAffectsRoute() {
        // Construct a graph with two alternative routes from 1 to 3.
        // Route 1: 1 -> 2 -> 3 ; Route 2: 1 -> 4 -> 3
        planner.addEdge(1, 2, 1000, 60);
        planner.addEdge(2, 3, 1000, 60);
        planner.addEdge(1, 4, 1200, 60);
        planner.addEdge(4, 3, 1200, 60);

        // Without traffic update, route 1 -> 2 -> 3 is faster.
        List<Integer> routeWithoutTraffic = planner.findFastestRoute(1, 3, 3600);
        assertNotNull(routeWithoutTraffic, "Route should not be null");
        assertEquals(Arrays.asList(1, 2, 3), routeWithoutTraffic, "Expected the direct route without traffic update");

        // Apply a traffic update on the road 1 -> 2 making it heavily congested between 3500 and 4000 seconds.
        TrafficUpdate update = new TrafficUpdate(1, 2, 3500, 4000, 3.0);
        planner.updateTraffic(update);

        // For departure time within the traffic update window, route 1->4->3 should be chosen.
        List<Integer> routeWithTraffic = planner.findFastestRoute(1, 3, 3600);
        assertNotNull(routeWithTraffic, "Route should not be null even with traffic update");
        assertEquals(Arrays.asList(1, 4, 3), routeWithTraffic, "Expected the alternate route due to congestion");

        // For departure time outside the traffic update window, the original route should be chosen.
        List<Integer> routeOutsideTraffic = planner.findFastestRoute(1, 3, 4100);
        assertNotNull(routeOutsideTraffic, "Route should not be null");
        assertEquals(Arrays.asList(1, 2, 3), routeOutsideTraffic, "Expected the direct route as traffic update is inactive");
    }

    @Test
    public void testOverlappingTrafficUpdatesAndInvalidUpdate() {
        // Construct a graph: 1 -> 2 -> 3
        planner.addEdge(1, 2, 1000, 60);
        planner.addEdge(2, 3, 1000, 60);

        // Apply first traffic update on 1 -> 2 between 3000 and 4000 with congestion factor 2.0
        TrafficUpdate update1 = new TrafficUpdate(1, 2, 3000, 4000, 2.0);
        planner.updateTraffic(update1);

        // Apply another overlapping traffic update on 1 -> 2 between 3500 and 4500 with congestion factor 2.5.
        TrafficUpdate update2 = new TrafficUpdate(1, 2, 3500, 4500, 2.5);
        planner.updateTraffic(update2);

        // Apply an invalid traffic update (non-positive congestion factor); should be ignored.
        TrafficUpdate invalidUpdate = new TrafficUpdate(1, 2, 3000, 4000, 0.0);
        planner.updateTraffic(invalidUpdate);

        // For departure in overlapping region, the worst congestion should apply.
        List<Integer> route = planner.findFastestRoute(1, 3, 3600);
        // Since there is only one route, it should still be [1, 2, 3]; however, the computed travel time should consider factor 2.5.
        // To verify the congestion effect, we might invoke a method to compute travel time.
        // Here, we simply assert that a route exists.
        assertNotNull(route, "Route should exist even with overlapping traffic updates");
        assertEquals(Arrays.asList(1, 2, 3), route, "Route remains unchanged even if travel time is affected");
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testConcurrentRouteRequests() throws InterruptedException {
        // Construct a basic graph for concurrency testing.
        planner.addEdge(1, 2, 800, 60);
        planner.addEdge(2, 3, 800, 60);
        planner.addEdge(3, 4, 800, 60);
        planner.addEdge(1, 4, 2500, 60);

        int numThreads = 50;
        CountDownLatch latch = new CountDownLatch(numThreads);
        Runnable task = () -> {
            try {
                // simulate concurrent requests with various departure times
                int departureTime = (int) (Math.random() * 5000);
                List<Integer> route = planner.findFastestRoute(1, 4, departureTime);
                // route should either be the multi-stop route or direct route.
                assertNotNull(route, "Route should not be null under concurrent requests");
                // Ensure the route starts at 1 and ends at 4
                assertEquals(1, route.get(0), "Route should start at node 1");
                assertEquals(4, route.get(route.size() - 1), "Route should end at node 4");
            } finally {
                latch.countDown();
            }
        };

        for (int i = 0; i < numThreads; i++) {
            new Thread(task).start();
        }

        // Wait for all threads to complete
        assertTrue(latch.await(5, TimeUnit.SECONDS), "All concurrent route requests should complete within timeout");
    }
}