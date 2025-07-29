package com.adaptivebalancer;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;
import java.util.HashSet;
import java.util.Set;
import java.util.Arrays;

public class AdaptiveBalancerTest {

    private AdaptiveBalancer balancer;

    @Before
    public void setup() {
        balancer = new AdaptiveBalancer();
        // Initialize with three backend servers with equal metrics.
        balancer.addBackend(new BackendServer("server1", 10, 100, 100));
        balancer.addBackend(new BackendServer("server2", 10, 100, 100));
        balancer.addBackend(new BackendServer("server3", 10, 100, 100));
    }

    @Test
    public void testBasicRouting() {
        // When all servers have equal metrics, routing should choose one of the active servers.
        Set<String> validServers = new HashSet<>(Arrays.asList("server1", "server2", "server3"));
        for (int i = 0; i < 10; i++) {
            String routedServer = balancer.routeRequest("req-" + i);
            assertTrue("Routed server should be one of the active servers",
                       validServers.contains(routedServer));
        }
    }

    @Test
    public void testLoadBasedRouting() {
        // Simulate diverse load and latency values.
        // server1: Overloaded and high latency, server2: light load and low latency, server3: moderate load.
        balancer.updateServerMetrics("server1", 90, 100, 150);
        balancer.updateServerMetrics("server2", 20, 100, 50);
        balancer.updateServerMetrics("server3", 50, 100, 100);
        
        // Expect routing to favor server2 most of the time.
        int countServer2 = 0;
        int totalRequests = 50;
        for (int i = 0; i < totalRequests; i++) {
            String routedServer = balancer.routeRequest("req-" + i);
            if ("server2".equals(routedServer)) {
                countServer2++;
            }
        }
        // At least 60% of requests should be routed to server2 under these conditions.
        assertTrue("Server2 should handle the majority of the requests", countServer2 >= 30);
    }

    @Test
    public void testHealthCheck() {
        // Mark server3 as unhealthy so that it should not receive any requests.
        balancer.updateServerHealth("server3", false);
        for (int i = 0; i < 20; i++) {
            String routedServer = balancer.routeRequest("req-health-" + i);
            assertNotEquals("Unhealthy server should not receive requests", "server3", routedServer);
        }
    }

    @Test
    public void testDynamicServerManagement() {
        // Remove server2 and verify that routing only considers server1 and server3.
        balancer.removeBackend("server2");
        Set<String> expectedServers = new HashSet<>(Arrays.asList("server1", "server3"));
        for (int i = 0; i < 10; i++) {
            String routedServer = balancer.routeRequest("req-dynamic-" + i);
            assertTrue("After removal, only server1 and server3 should receive requests",
                       expectedServers.contains(routedServer));
        }

        // Dynamically add a new server and verify it is included in the routing.
        balancer.addBackend(new BackendServer("server4", 5, 100, 30));
        expectedServers.add("server4");
        for (int i = 0; i < 20; i++) {
            String routedServer = balancer.routeRequest("req-dynamic-add-" + i);
            assertTrue("Newly added server4 should be considered in routing",
                       expectedServers.contains(routedServer));
        }
    }

    @Test
    public void testPerformanceMetrics() {
        // Simulate processing a series of requests with varying metrics.
        int totalRequests = 100;
        for (int i = 0; i < totalRequests; i++) {
            // Update server1 metrics to simulate dynamic load and latency.
            int load = 10 + (i % 20);
            int latency = 100 + (i % 50);
            balancer.updateServerMetrics("server1", load, 100, latency);
            balancer.routeRequest("req-perf-" + i);
        }
        // Retrieve and verify performance statistics.
        long avgLatency = balancer.getAverageLatency();
        long throughput = balancer.getThroughput();
        assertTrue("Average latency should be greater than zero", avgLatency > 0);
        assertTrue("Throughput should be greater than zero", throughput > 0);
    }
}