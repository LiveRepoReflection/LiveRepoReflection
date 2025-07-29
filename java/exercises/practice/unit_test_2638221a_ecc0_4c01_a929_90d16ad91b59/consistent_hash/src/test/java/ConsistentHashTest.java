import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static org.junit.jupiter.api.Assertions.*;

public class ConsistentHashTest {
    private ConsistentHashLoadBalancer loadBalancer;

    @BeforeEach
    public void setUp() {
        loadBalancer = new ConsistentHashLoadBalancer();
    }

    @Test
    public void testAddServer() {
        assertTrue(loadBalancer.addServer("server1", 1));
        assertTrue(loadBalancer.addServer("server2", 2));
        assertTrue(loadBalancer.addServer("server3", 3));
        
        // Adding duplicate server should fail
        assertFalse(loadBalancer.addServer("server1", 1));
    }

    @Test
    public void testRemoveServer() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 2);
        
        assertTrue(loadBalancer.removeServer("server1"));
        assertFalse(loadBalancer.removeServer("server1")); // Already removed
        assertFalse(loadBalancer.removeServer("nonexistent")); // Never existed
    }

    @Test
    public void testGetServerWithEmptyCluster() {
        assertThrows(IllegalStateException.class, () -> loadBalancer.getServer("anyKey"));
    }

    @Test
    public void testGetServerWithSingleServer() {
        loadBalancer.addServer("server1", 1);
        assertEquals("server1", loadBalancer.getServer("key1"));
        assertEquals("server1", loadBalancer.getServer("key2"));
    }

    @Test
    public void testNullOrEmptyKey() {
        loadBalancer.addServer("server1", 1);
        
        assertThrows(IllegalArgumentException.class, () -> loadBalancer.getServer(null));
        // Empty keys should be valid but might throw in some implementations
        try {
            loadBalancer.getServer("");
        } catch (IllegalArgumentException e) {
            // This is acceptable but not required
        }
    }

    @Test
    public void testInvalidServerWeight() {
        assertThrows(IllegalArgumentException.class, () -> loadBalancer.addServer("server1", 0));
        assertThrows(IllegalArgumentException.class, () -> loadBalancer.addServer("server2", -1));
    }

    @Test
    public void testConsistencyWhenAddingServer() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 1);
        
        // Generate sample keys and track their initial assignment
        Map<String, String> initialAssignments = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String key = "key" + i;
            initialAssignments.put(key, loadBalancer.getServer(key));
        }
        
        // Add a new server
        loadBalancer.addServer("server3", 1);
        
        // Count keys that got remapped
        int remappedCount = 0;
        for (int i = 0; i < 1000; i++) {
            String key = "key" + i;
            if (!loadBalancer.getServer(key).equals(initialAssignments.get(key))) {
                remappedCount++;
            }
        }
        
        // With consistent hashing, we expect significantly fewer than 2/3 of keys to be remapped
        // Ideally around 1/3 of keys should be remapped to the new server
        assertTrue(remappedCount < 500, "Too many keys were remapped: " + remappedCount);
    }

    @Test
    public void testConsistencyWhenRemovingServer() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 1);
        loadBalancer.addServer("server3", 1);
        
        // Generate sample keys and track their initial assignment
        Map<String, String> initialAssignments = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String key = "key" + i;
            initialAssignments.put(key, loadBalancer.getServer(key));
        }
        
        // Remove a server
        loadBalancer.removeServer("server1");
        
        // Count keys that got remapped
        int remappedCount = 0;
        for (int i = 0; i < 1000; i++) {
            String key = "key" + i;
            String oldServer = initialAssignments.get(key);
            String newServer = loadBalancer.getServer(key);
            
            if (!newServer.equals(oldServer)) {
                remappedCount++;
                // Keys assigned to the removed server must be remapped
                if (oldServer.equals("server1")) {
                    assertTrue(true);
                } else {
                    // Keys not assigned to removed server should stay the same
                    fail("Key " + key + " was remapped from " + oldServer + " to " + newServer);
                }
            }
        }
        
        // Only keys previously assigned to server1 should be remapped
        assertTrue(remappedCount < 500, "Too many keys were remapped: " + remappedCount);
    }

    @Test
    public void testLoadDistribution() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 1);
        loadBalancer.addServer("server3", 1);
        
        Map<String, Integer> serverCounts = new HashMap<>();
        
        // Generate a large number of random keys
        for (int i = 0; i < 10000; i++) {
            String key = UUID.randomUUID().toString();
            String server = loadBalancer.getServer(key);
            serverCounts.put(server, serverCounts.getOrDefault(server, 0) + 1);
        }
        
        // Check that each server gets approximately 1/3 of the keys
        for (String server : serverCounts.keySet()) {
            int count = serverCounts.get(server);
            double percentage = count / 10000.0;
            assertTrue(percentage > 0.25 && percentage < 0.4, 
                    server + " got " + percentage + " of keys, expected around 0.33");
        }
    }
    
    @Test
    public void testWeightedLoadDistribution() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 2);
        loadBalancer.addServer("server3", 3);
        
        Map<String, Integer> serverCounts = new HashMap<>();
        
        // Generate a large number of random keys
        for (int i = 0; i < 10000; i++) {
            String key = UUID.randomUUID().toString();
            String server = loadBalancer.getServer(key);
            serverCounts.put(server, serverCounts.getOrDefault(server, 0) + 1);
        }
        
        // Check that servers get keys proportional to their weights
        int total = serverCounts.values().stream().mapToInt(Integer::intValue).sum();
        
        double server1Percentage = serverCounts.getOrDefault("server1", 0) / (double) total;
        double server2Percentage = serverCounts.getOrDefault("server2", 0) / (double) total;
        double server3Percentage = serverCounts.getOrDefault("server3", 0) / (double) total;
        
        // Allow some tolerance in distribution
        assertTrue(server1Percentage > 0.10 && server1Percentage < 0.25, 
                "server1 got " + server1Percentage + " of keys, expected around 0.17");
        assertTrue(server2Percentage > 0.25 && server2Percentage < 0.40, 
                "server2 got " + server2Percentage + " of keys, expected around 0.33");
        assertTrue(server3Percentage > 0.40 && server3Percentage < 0.55, 
                "server3 got " + server3Percentage + " of keys, expected around 0.50");
    }

    @Test
    public void testConcurrencyHandling() throws InterruptedException {
        for (int i = 1; i <= 5; i++) {
            loadBalancer.addServer("server" + i, i);
        }
        
        int numThreads = 10;
        int operationsPerThread = 1000;
        CountDownLatch latch = new CountDownLatch(numThreads);
        ExecutorService executorService = Executors.newFixedThreadPool(numThreads);
        AtomicInteger exceptions = new AtomicInteger(0);
        
        for (int i = 0; i < numThreads; i++) {
            final int threadId = i;
            executorService.submit(() -> {
                try {
                    Random random = new Random();
                    for (int j = 0; j < operationsPerThread; j++) {
                        int operation = random.nextInt(3);
                        
                        if (operation == 0) {
                            // Add server
                            String serverId = "server" + threadId + "_" + j;
                            try {
                                loadBalancer.addServer(serverId, random.nextInt(5) + 1);
                            } catch (Exception e) {
                                // Ignore expected exceptions (duplicate servers)
                            }
                        } else if (operation == 1) {
                            // Remove server
                            try {
                                loadBalancer.removeServer("server" + (random.nextInt(5) + 1));
                            } catch (Exception e) {
                                // Ignore expected exceptions (server not found)
                            }
                        } else {
                            // Get server
                            try {
                                String key = "key" + random.nextInt(1000);
                                loadBalancer.getServer(key);
                            } catch (IllegalStateException e) {
                                // This can happen if all servers were removed
                            } catch (Exception e) {
                                exceptions.incrementAndGet();
                            }
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        assertTrue(latch.await(30, TimeUnit.SECONDS), "Threads did not complete in time");
        executorService.shutdown();
        
        assertEquals(0, exceptions.get(), "Unexpected exceptions occurred");
    }
    
    @Test
    public void testLargeNumberOfServers() {
        // Add 500 servers
        for (int i = 1; i <= 500; i++) {
            loadBalancer.addServer("server" + i, 1);
        }
        
        // Test with 10000 keys
        Map<String, Integer> serverCounts = new HashMap<>();
        for (int i = 0; i < 10000; i++) {
            String key = "key" + i;
            String server = loadBalancer.getServer(key);
            serverCounts.put(server, serverCounts.getOrDefault(server, 0) + 1);
        }
        
        // With consistent hashing and virtual nodes, we expect a reasonably even distribution
        // Calculate standard deviation to measure distribution evenness
        double mean = 10000.0 / 500; // Expected average
        double sumOfSquaredDifferences = 0;
        
        for (int count : serverCounts.values()) {
            double difference = count - mean;
            sumOfSquaredDifferences += difference * difference;
        }
        
        double stdDev = Math.sqrt(sumOfSquaredDifferences / 500);
        double relativeStdDev = stdDev / mean; // Coefficient of variation
        
        // For a good implementation, relative std dev should be small (typically < 0.25)
        assertTrue(relativeStdDev < 0.3, "Distribution not even enough, relative std dev: " + relativeStdDev);
    }
    
    @Test
    public void testHashRingWraparound() {
        loadBalancer.addServer("server1", 1);
        loadBalancer.addServer("server2", 1);
        
        // We can't directly test the wraparound since we don't know the hash values,
        // but we can ensure that all keys get assigned somewhere
        for (int i = 0; i < 1000; i++) {
            String key = "key" + i;
            assertNotNull(loadBalancer.getServer(key));
        }
    }
}