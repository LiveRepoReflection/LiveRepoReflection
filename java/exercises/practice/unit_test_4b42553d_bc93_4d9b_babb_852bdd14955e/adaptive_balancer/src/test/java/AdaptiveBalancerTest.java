import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class AdaptiveBalancerTest {

    private AdaptiveBalancer loadBalancer;

    @BeforeEach
    public void setup() {
        loadBalancer = new AdaptiveBalancer();
    }

    @Test
    public void testRegisterAndRouteRequest() {
        // Create two servers with different capacities and latencies.
        Server server1 = new Server("srv1", 5, 50); // id, capacity, latency
        Server server2 = new Server("srv2", 10, 100);
        loadBalancer.registerServer(server1);
        loadBalancer.registerServer(server2);

        // Create a request with medium priority.
        Request req = new Request("req1", Priority.MEDIUM);
        String routedServerId = loadBalancer.routeRequest(req);
        
        // The request should be routed to one of the healthy registered servers.
        boolean validRouting = routedServerId.equals("srv1") || routedServerId.equals("srv2");
        assertTrue(validRouting, "Request should be routed to one of the registered servers.");
    }

    @Test
    public void testHealthCheckRemoval() {
        // Register two servers.
        Server server1 = new Server("srv1", 5, 50);
        Server server2 = new Server("srv2", 10, 100);
        loadBalancer.registerServer(server1);
        loadBalancer.registerServer(server2);

        // Simulate a health check failure on server1.
        loadBalancer.updateServerHealth("srv1", false);

        // Test that only server2 receives new requests.
        Request req = new Request("req2", Priority.HIGH);
        String routedServerId = loadBalancer.routeRequest(req);
        assertEquals("srv2", routedServerId, "Only healthy servers should receive requests.");

        // Recover server1 and test that routing can be performed on either.
        loadBalancer.updateServerHealth("srv1", true);
        routedServerId = loadBalancer.routeRequest(req);
        boolean validRouting = routedServerId.equals("srv1") || routedServerId.equals("srv2");
        assertTrue(validRouting, "After health recovery, request should be routed to a healthy server.");
    }

    @Test
    public void testRequestPrioritization() {
        // Register three servers with varying capacities and latencies.
        Server server1 = new Server("srv1", 5, 50);
        Server server2 = new Server("srv2", 10, 100);
        Server server3 = new Server("srv3", 7, 30); // lower latency
        loadBalancer.registerServer(server1);
        loadBalancer.registerServer(server2);
        loadBalancer.registerServer(server3);

        // Artificially ramp up the load on server3.
        loadBalancer.updateServerLoad("srv3", 7); // max load equals capacity

        // Send a high-priority request expecting it to avoid heavily loaded server3.
        Request highPriorityReq = new Request("req_high", Priority.HIGH);
        String routedServerId = loadBalancer.routeRequest(highPriorityReq);
        boolean validHighPriorityRouting = routedServerId.equals("srv1") || routedServerId.equals("srv2");
        assertTrue(validHighPriorityRouting, "High priority requests should not be routed to overloaded servers.");

        // Send a low-priority request that may be routed to any server.
        Request lowPriorityReq = new Request("req_low", Priority.LOW);
        routedServerId = loadBalancer.routeRequest(lowPriorityReq);
        boolean validLowPriorityRouting = routedServerId.equals("srv1") || routedServerId.equals("srv2") || routedServerId.equals("srv3");
        assertTrue(validLowPriorityRouting, "Low priority requests can be routed to any server.");
    }

    @Test
    public void testOverloadProtection() {
        // Register a single server with limited capacity.
        Server server1 = new Server("srv1", 3, 50);
        loadBalancer.registerServer(server1);

        // Bring server1 to full load.
        loadBalancer.updateServerLoad("srv1", 3); // Load equals its capacity

        // Sending a new request should result in a rejection.
        Request req = new Request("req_overload", Priority.MEDIUM);
        String routedServerId = loadBalancer.routeRequest(req);
        assertEquals("REJECTED", routedServerId, "Requests should be rejected if server capacity is full.");
    }

    @Test
    public void testDynamicServerDiscovery() {
        // Initially no server is registered so the request should be rejected.
        Request req = new Request("req_initial", Priority.MEDIUM);
        String routedServerId = loadBalancer.routeRequest(req);
        assertEquals("REJECTED", routedServerId, "If no servers are available, request should be rejected.");

        // Dynamically add a server.
        Server server1 = new Server("srv1", 5, 40);
        loadBalancer.registerServer(server1);
        routedServerId = loadBalancer.routeRequest(req);
        assertEquals("srv1", routedServerId, "After registering a server, request should be routed to it.");

        // Dynamically remove the server.
        loadBalancer.deregisterServer("srv1");
        routedServerId = loadBalancer.routeRequest(req);
        assertEquals("REJECTED", routedServerId, "After deregistering, request should be rejected.");
    }
}