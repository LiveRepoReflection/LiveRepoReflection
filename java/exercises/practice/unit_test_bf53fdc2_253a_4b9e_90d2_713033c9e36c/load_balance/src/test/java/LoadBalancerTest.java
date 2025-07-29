import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class LoadBalancerTest {

    private LoadBalancer loadBalancer;

    @BeforeEach
    public void setup() {
        // This setup is intentionally left blank.
        // Specific tests will initialize the LoadBalancer with appropriate capacity arrays.
    }

    @Test
    public void testRouteToAvailableServer() {
        // Given a capacity array with available servers at indices 0 and 2.
        int[] capacities = {2, 0, 5};
        loadBalancer = new LoadBalancer(capacities);
        int server = loadBalancer.routeRequest(5, 0, 10);
        // The returned server index must correspond to a server that has a positive capacity.
        assertTrue(server == 0 || server == 2, "The returned server should be one with available capacity.");
    }

    @Test
    public void testRouteWhenNoServerAvailable() {
        // Given a capacity array with no available servers.
        int[] capacities = {0, 0, 0};
        loadBalancer = new LoadBalancer(capacities);
        int server = loadBalancer.routeRequest(5, 0, 10);
        // Expect -1 since the request should be queued.
        assertEquals(-1, server, "When no server has capacity, the request must be queued and -1 returned.");
    }

    @Test
    public void testMultipleRequestsAndQueueProcessing() {
        // Start with no capacity so that requests will be queued.
        int[] initialCapacities = {0, 0, 0};
        loadBalancer = new LoadBalancer(initialCapacities);
        // Two requests arriving at time = 0 and 0 respectively.
        int server1 = loadBalancer.routeRequest(8, 0, 5);
        int server2 = loadBalancer.routeRequest(3, 0, 5);
        assertEquals(-1, server1, "First request should be queued when no server is available.");
        assertEquals(-1, server2, "Second request should be queued when no server is available.");
        
        // Update capacity to make a server available.
        int[] updatedCapacities = {1, 0, 0};
        loadBalancer.updateCapacity(updatedCapacities);
        // Process queued requests at time = 3.
        int processedServer = loadBalancer.processQueue(3);
        assertEquals(0, processedServer, "Queued request should be processed and assigned to server index 0.");
    }

    @Test
    public void testStarvationPromotion() {
        // Start with all servers exhausted.
        int[] initialCapacities = {0, 0};
        loadBalancer = new LoadBalancer(initialCapacities);
        // A low-priority request arrives at time = 0 and is queued.
        int lowPriorityRequest = loadBalancer.routeRequest(1, 0, 5);
        assertEquals(-1, lowPriorityRequest, "Low priority request should be queued when no capacity is available.");
        
        // Simulate time passing beyond the starvation threshold and update capacity.
        int[] updatedCapacities = {0, 1};
        loadBalancer.updateCapacity(updatedCapacities);
        // Process the queue at time = 6 (which is > arrival time + starvationThreshold).
        int processedServer = loadBalancer.processQueue(6);
        assertEquals(1, processedServer, "The low priority request should be promoted due to starvation and assigned to server index 1.");
    }

    @Test
    public void testConcurrentRequestsOrdering() {
        // Given three servers each with a capacity of 1.
        int[] capacities = {1, 1, 1};
        loadBalancer = new LoadBalancer(capacities);
        // Three requests with the same priority and increasing arrival times.
        int server1 = loadBalancer.routeRequest(5, 1, 5);
        int server2 = loadBalancer.routeRequest(5, 2, 5);
        int server3 = loadBalancer.routeRequest(5, 3, 5);
        
        // Each request should be processed immediately and assigned to a unique server.
        assertNotEquals(-1, server1, "First request should be assigned to an available server.");
        assertNotEquals(-1, server2, "Second request should be assigned to an available server.");
        assertNotEquals(-1, server3, "Third request should be assigned to an available server.");
        
        // The three servers should be distinct.
        assertNotEquals(server1, server2, "Server assignments should be unique for concurrent requests.");
        assertNotEquals(server1, server3, "Server assignments should be unique for concurrent requests.");
        assertNotEquals(server2, server3, "Server assignments should be unique for concurrent requests.");
    }
}