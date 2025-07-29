package route_optim;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class RouteOptimTest {

    @Test
    public void testDirectRoute() {
        // Graph: 1 -> 2
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(new RouteOptim.Edge(2, 10, 5)));
        graph.put(2, new ArrayList<>());

        // Single delivery request from 1 to 2 with priority 5
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 2, 5));

        int drivers = 1;
        int maxDuration = 20;
        int congestionThreshold = 10;
        double alpha = 0.5;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);
        
        assertNotNull(routes);
        assertEquals(1, routes.size());
        List<Integer> route = routes.get(0);
        List<Integer> expected = Arrays.asList(1, 2);
        assertEquals(expected, route);
    }

    @Test
    public void testMultiplePathsSelectsValidRoute() {
        // Graph:
        // 1 -> 2 (travel=5, congestion=10)
        // 2 -> 3 (travel=5, congestion=10)
        // 1 -> 3 (travel=10, congestion=50)
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(
                new RouteOptim.Edge(2, 5, 10),
                new RouteOptim.Edge(3, 10, 50)
        ));
        graph.put(2, Arrays.asList(new RouteOptim.Edge(3, 5, 10)));
        graph.put(3, new ArrayList<>());

        // Single delivery request from 1 to 3, priority 7
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 3, 7));

        int drivers = 1;
        int maxDuration = 20;
        int congestionThreshold = 100;
        double alpha = 0.5;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(1, routes.size());
        List<Integer> route = routes.get(0);
        // Expected route is [1,2,3] because it minimizes weighted sum over the direct edge.
        List<Integer> expected = Arrays.asList(1, 2, 3);
        assertEquals(expected, route);
    }

    @Test
    public void testNoValidRoute() {
        // Graph: 1 -> 2 only, no connection to 3.
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(new RouteOptim.Edge(2, 10, 5)));
        graph.put(2, new ArrayList<>());
        // Node 3 exists but has no incoming edges
        graph.put(3, new ArrayList<>());

        // Request from 1 to 3, priority 3
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 3, 3));

        int drivers = 1;
        int maxDuration = 50;
        int congestionThreshold = 20;
        double alpha = 0.5;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(1, routes.size());
        // Expect an empty route since 3 is unreachable.
        assertTrue(routes.get(0).isEmpty());
    }

    @Test
    public void testSameStartAndEnd() {
        // Graph: Even an empty graph works because start and end are same.
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, new ArrayList<>());
        graph.put(2, new ArrayList<>());

        // Request where start and end are the same (node 2), priority 4
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(2, 2, 4));

        int drivers = 1;
        int maxDuration = 10;
        int congestionThreshold = 5;
        double alpha = 0.5;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(1, routes.size());
        // The optimal route should be a single node [2]
        List<Integer> expected = Arrays.asList(2);
        assertEquals(expected, routes.get(0));
    }

    @Test
    public void testDurationConstraint() {
        // Graph:
        // 1 -> 2 (travel=100, congestion=5)
        // 2 -> 3 (travel=100, congestion=5)
        // Alternative path:
        // 1 -> 4 (travel=50, congestion=5)
        // 4 -> 3 (travel=50, congestion=5)
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(
                new RouteOptim.Edge(2, 100, 5),
                new RouteOptim.Edge(4, 50, 5)
        ));
        graph.put(2, Arrays.asList(new RouteOptim.Edge(3, 100, 5)));
        graph.put(4, Arrays.asList(new RouteOptim.Edge(3, 50, 5)));
        graph.put(3, new ArrayList<>());

        // Request from 1 to 3, priority 6
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 3, 6));

        int drivers = 1;
        // Set maxDuration such that the longer route 1->2->3 is invalid (200 > 150) but 1->4->3 is valid (100 <= 150).
        int maxDuration = 150;
        int congestionThreshold = 20;
        double alpha = 0.7;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(1, routes.size());
        // Expect the route [1,4,3]
        List<Integer> expected = Arrays.asList(1, 4, 3);
        assertEquals(expected, routes.get(0));
    }

    @Test
    public void testCongestionConstraint() {
        // Graph:
        // 1 -> 2 (travel=10, congestion=3000)
        // 2 -> 3 (travel=10, congestion=3000)
        // Alternative path:
        // 1 -> 4 (travel=20, congestion=1000)
        // 4 -> 3 (travel=20, congestion=1000)
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(
                new RouteOptim.Edge(2, 10, 3000),
                new RouteOptim.Edge(4, 20, 1000)
        ));
        graph.put(2, Arrays.asList(new RouteOptim.Edge(3, 10, 3000)));
        graph.put(4, Arrays.asList(new RouteOptim.Edge(3, 20, 1000)));
        graph.put(3, new ArrayList<>());

        // Request from 1 to 3, priority 8
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 3, 8));

        int drivers = 1;
        int maxDuration = 100;
        // Set congestionThreshold to 2500, so the route 1->2->3 (congestion=6000) is invalid.
        int congestionThreshold = 2500;
        double alpha = 0.3;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(1, routes.size());
        // Expect the route [1,4,3]
        List<Integer> expected = Arrays.asList(1, 4, 3);
        assertEquals(expected, routes.get(0));
    }

    @Test
    public void testMultipleRequests() {
        // Graph:
        // 1 -> 2, 2 -> 3, 1 -> 4, 4 -> 5, 5 -> 3
        Map<Integer, List<RouteOptim.Edge>> graph = new HashMap<>();
        graph.put(1, Arrays.asList(
                new RouteOptim.Edge(2, 15, 5),
                new RouteOptim.Edge(4, 10, 10)
        ));
        graph.put(2, Arrays.asList(new RouteOptim.Edge(3, 15, 5)));
        graph.put(4, Arrays.asList(new RouteOptim.Edge(5, 10, 10)));
        graph.put(5, Arrays.asList(new RouteOptim.Edge(3, 10, 5)));
        graph.put(3, new ArrayList<>());

        // Two requests:
        // Request 1: from 1 to 3, priority 9 -> Expected best route: [1,2,3] or [1,4,5,3] depending on weights.
        // Request 2: from 4 to 3, priority 4 -> Only valid route: [4,5,3]
        List<RouteOptim.DeliveryRequest> requests = new ArrayList<>();
        requests.add(new RouteOptim.DeliveryRequest(1, 3, 9));
        requests.add(new RouteOptim.DeliveryRequest(4, 3, 4));

        int drivers = 2;
        int maxDuration = 50;
        int congestionThreshold = 30;
        double alpha = 0.6;

        List<List<Integer>> routes = new RouteOptim().findOptimalRoutes(graph, requests, drivers, maxDuration, congestionThreshold, alpha);

        assertNotNull(routes);
        assertEquals(2, routes.size());

        // Validate that each route starts with the correct start node and ends with the correct end node
        List<Integer> route1 = routes.get(0);
        List<Integer> route2 = routes.get(1);
        assertFalse(route1.isEmpty());
        assertFalse(route2.isEmpty());
        assertEquals(Integer.valueOf(1), route1.get(0));
        assertEquals(Integer.valueOf(3), route1.get(route1.size() - 1));
        assertEquals(Integer.valueOf(4), route2.get(0));
        assertEquals(Integer.valueOf(3), route2.get(route2.size() - 1));
    }
}