import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class NetworkRoutingTest {

    @Test
    public void testSingleContentServed() {
        // Construct network topology: Two servers with one edge between them.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10));

        // Define server capacities.
        Map<Integer, Integer> serverCapacities = new HashMap<>();
        serverCapacities.put(1, 1);
        serverCapacities.put(2, 1);

        // Define content location: Content "A" is available only on server 2.
        Map<String, List<Integer>> contentLocation = new HashMap<>();
        contentLocation.put("A", Arrays.asList(2));

        // A single content request originating from server 1 for content "A".
        List<ContentRequest> contentRequests = new ArrayList<>();
        contentRequests.add(new ContentRequest(1, "A"));

        NetworkRouting routingSystem = new NetworkRouting(edges, serverCapacities, contentLocation);
        List<RoutingDecision> decisions = routingSystem.routeRequests(contentRequests);

        assertEquals(1, decisions.size());
        RoutingDecision decision = decisions.get(0);
        // Expect the request to be routed to server 2 and served.
        assertEquals(0, decision.getRequestId());
        assertEquals(2, decision.getServerId());
        assertEquals("served", decision.getStatus());
    }

    @Test
    public void testDroppedContentWhenUnavailable() {
        // Construct network topology: Single server.
        List<Edge> edges = new ArrayList<>();

        Map<Integer, Integer> serverCapacities = new HashMap<>();
        serverCapacities.put(1, 1);

        // Content "B" is not available on any server.
        Map<String, List<Integer>> contentLocation = new HashMap<>();

        // A single content request from server 1 for content "B".
        List<ContentRequest> contentRequests = Collections.singletonList(new ContentRequest(1, "B"));

        NetworkRouting routingSystem = new NetworkRouting(edges, serverCapacities, contentLocation);
        List<RoutingDecision> decisions = routingSystem.routeRequests(contentRequests);

        assertEquals(1, decisions.size());
        RoutingDecision decision = decisions.get(0);
        // Expect the request to be dropped.
        assertEquals(0, decision.getRequestId());
        assertEquals(-1, decision.getServerId());
        assertEquals("dropped", decision.getStatus());
    }

    @Test
    public void testMultipleCandidatesWithDifferentLatencies() {
        // Construct network topology with four servers.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 5));
        edges.add(new Edge(2, 3, 15));
        edges.add(new Edge(1, 4, 20));
        edges.add(new Edge(4, 3, 5));
        edges.add(new Edge(2, 4, 10));

        Map<Integer, Integer> serverCapacities = new HashMap<>();
        serverCapacities.put(1, 1);
        serverCapacities.put(2, 1);
        serverCapacities.put(3, 1);
        serverCapacities.put(4, 1);

        // Content "C" is hosted on both server 3 and server 4.
        Map<String, List<Integer>> contentLocation = new HashMap<>();
        contentLocation.put("C", Arrays.asList(3, 4));

        // A single request originating from server 1 for content "C".
        List<ContentRequest> contentRequests = Collections.singletonList(new ContentRequest(1, "C"));

        NetworkRouting routingSystem = new NetworkRouting(edges, serverCapacities, contentLocation);
        List<RoutingDecision> decisions = routingSystem.routeRequests(contentRequests);

        assertEquals(1, decisions.size());
        RoutingDecision decision = decisions.get(0);
        // Expected outcome: The system should choose the server with the lower latency route.
        // Route possibilities: 1->2->3 = 20 OR 1->4->3 = 25 OR 1->4 = 20.
        // Acceptable answer is either server 3 or 4 if tied; here we check that a valid server is chosen.
        assertEquals(0, decision.getRequestId());
        assertTrue(decision.getServerId() == 3 || decision.getServerId() == 4);
        assertEquals("served", decision.getStatus());
    }

    @Test
    public void testLoadBalancingAcrossServers() {
        // Construct a network topology with three interconnected servers.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 10));
        edges.add(new Edge(2, 3, 10));
        edges.add(new Edge(1, 3, 20));

        // Set server capacities where server 2 has very limited capacity.
        Map<Integer, Integer> serverCapacities = new HashMap<>();
        serverCapacities.put(1, 2);
        serverCapacities.put(2, 1);
        serverCapacities.put(3, 2);

        // Content "D" is available on both server 2 and server 3.
        Map<String, List<Integer>> contentLocation = new HashMap<>();
        contentLocation.put("D", Arrays.asList(2, 3));

        // Two requests originating from server 1 for content "D".
        List<ContentRequest> contentRequests = new ArrayList<>();
        contentRequests.add(new ContentRequest(1, "D"));
        contentRequests.add(new ContentRequest(1, "D"));

        NetworkRouting routingSystem = new NetworkRouting(edges, serverCapacities, contentLocation);
        List<RoutingDecision> decisions = routingSystem.routeRequests(contentRequests);

        // Depending on load balancing mechanism, the first request might go to server 2 (shortest path) and the second to server 3.
        assertEquals(2, decisions.size());
        RoutingDecision firstDecision = decisions.get(0);
        RoutingDecision secondDecision = decisions.get(1);

        // Validate that one request is served by server 2 and the other is served by server 3.
        List<Integer> chosenServers = Arrays.asList(firstDecision.getServerId(), secondDecision.getServerId());
        assertTrue(chosenServers.contains(2));
        assertTrue(chosenServers.contains(3));
        assertEquals("served", firstDecision.getStatus());
        assertEquals("served", secondDecision.getStatus());
    }

    @Test
    public void testDynamicServerCapacityAdjustments() {
        // Construct a simple network with two servers.
        List<Edge> edges = new ArrayList<>();
        edges.add(new Edge(1, 2, 5));

        // Initial capacities: server 2 can only handle 1 request.
        Map<Integer, Integer> serverCapacities = new HashMap<>();
        serverCapacities.put(1, 1);
        serverCapacities.put(2, 1);

        // Content "E" available on server 2.
        Map<String, List<Integer>> contentLocation = new HashMap<>();
        contentLocation.put("E", Arrays.asList(2));

        // Process first batch: Two requests from server 1.
        List<ContentRequest> firstBatch = new ArrayList<>();
        firstBatch.add(new ContentRequest(1, "E"));
        firstBatch.add(new ContentRequest(1, "E"));

        NetworkRouting routingSystem = new NetworkRouting(edges, serverCapacities, contentLocation);
        List<RoutingDecision> firstDecisions = routingSystem.routeRequests(firstBatch);

        // First request should be served and the second should be dropped because capacity of server 2 is exhausted.
        assertEquals(2, firstDecisions.size());
        RoutingDecision decision1 = firstDecisions.get(0);
        RoutingDecision decision2 = firstDecisions.get(1);
        assertEquals("served", decision1.getStatus());
        assertEquals("dropped", decision2.getStatus());

        // Simulate dynamic capacity update: Increase capacity for server 2.
        serverCapacities.put(2, 2);
        routingSystem.updateServerCapacities(serverCapacities);

        // Process second batch: One request from server 1.
        List<ContentRequest> secondBatch = Collections.singletonList(new ContentRequest(1, "E"));
        List<RoutingDecision> secondDecisions = routingSystem.routeRequests(secondBatch);
        assertEquals(1, secondDecisions.size());
        RoutingDecision decision3 = secondDecisions.get(0);
        assertEquals("served", decision3.getStatus());
        assertEquals(2, decision3.getServerId());
    }
}