import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.*;

public class NetworkReconstructionTest {
    private NetworkReconstruction networkReconstruction;

    @BeforeEach
    public void setup() {
        networkReconstruction = new NetworkReconstruction();
    }

    @Test
    public void testWithEmptyLog() {
        int n = 3;
        List<LogEntry> log = new ArrayList<>();
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        assertThat(result).hasSize(n);
        for (int i = 1; i <= n; i++) {
            assertThat(result).containsKey(i);
            // In a complete graph, each node is connected to every other node
            assertEquals(n - 1, result.get(i).size());
            for (int j = 1; j <= n; j++) {
                if (i != j) {
                    assertThat(result.get(i)).contains(j);
                }
            }
        }
    }

    @Test
    public void testWithGivenExample() {
        int n = 4;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1678886400L, 1, 2),
            new LogEntry(1678886401L, 2, 3)
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        for (int i = 1; i <= n; i++) {
            assertThat(result).containsKey(i);
        }

        // Verify connections from the log are present
        assertThat(result.get(1)).contains(2);
        assertThat(result.get(2)).contains(1);
        assertThat(result.get(2)).contains(3);
        assertThat(result.get(3)).contains(2);

        // Check that the graph is connected and minimizes average path length
        // For this example, the optimal solution should have connections:
        // 1-2, 2-3, 1-4, 3-4 or equivalently 1-2, 2-3, 1-4, 2-4
        // Verify that we have an undirected graph (if a is connected to b, b is connected to a)
        for (int i = 1; i <= n; i++) {
            for (int j : result.get(i)) {
                assertThat(result.get(j)).contains(i);
            }
        }

        // Check average path length is minimized
        double avgPathLength = calculateAveragePathLength(result, n);
        assertThat(avgPathLength).isLessThanOrEqualTo(1.5); // In this optimized network
    }

    @Test
    public void testWithFullyConnectedNetwork() {
        int n = 5;
        List<LogEntry> log = new ArrayList<>();
        
        // Add all possible connections
        for (int i = 1; i <= n; i++) {
            for (int j = i + 1; j <= n; j++) {
                log.add(new LogEntry(10000L + i * 100 + j, i, j));
            }
        }
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        
        // Verify every node is connected to every other node
        for (int i = 1; i <= n; i++) {
            assertThat(result.get(i)).hasSize(n - 1);
            for (int j = 1; j <= n; j++) {
                if (i != j) {
                    assertThat(result.get(i)).contains(j);
                }
            }
        }
    }

    @Test
    public void testWithChainNetwork() {
        int n = 5;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 2),
            new LogEntry(1001L, 2, 3),
            new LogEntry(1002L, 3, 4),
            new LogEntry(1003L, 4, 5)
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        
        // Verify connections from the log are present
        assertThat(result.get(1)).contains(2);
        assertThat(result.get(2)).contains(1, 3);
        assertThat(result.get(3)).contains(2, 4);
        assertThat(result.get(4)).contains(3, 5);
        assertThat(result.get(5)).contains(4);
        
        // Additional connections should be added to minimize average path length
        // The optimal solution may add additional edges like 1-5, 1-3, 1-4, 2-4, 2-5, 3-5
        // Check average path length
        double avgPathLength = calculateAveragePathLength(result, n);
        double chainAvgPathLength = 2.0; // Average path length in a chain of 5 nodes
        assertThat(avgPathLength).isLessThanOrEqualTo(chainAvgPathLength);
    }

    @Test
    public void testWithStarNetwork() {
        int n = 5;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 2),
            new LogEntry(1001L, 1, 3),
            new LogEntry(1002L, 1, 4),
            new LogEntry(1003L, 1, 5)
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        
        // Verify connections from the log are present
        assertThat(result.get(1)).contains(2, 3, 4, 5);
        assertThat(result.get(2)).contains(1);
        assertThat(result.get(3)).contains(1);
        assertThat(result.get(4)).contains(1);
        assertThat(result.get(5)).contains(1);
        
        // Additional connections should be added to minimize average path length
        // For a star, additional edges might be added like 2-3, 2-4, 2-5, 3-4, 3-5, 4-5
        // Check average path length
        double avgPathLength = calculateAveragePathLength(result, n);
        double starAvgPathLength = 1.6; // Average path length in a star of 5 nodes
        assertThat(avgPathLength).isLessThanOrEqualTo(starAvgPathLength);
    }

    @Test
    public void testWithIsolatedServers() {
        int n = 4;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 2)
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        
        // Verify connections from the log are present
        assertThat(result.get(1)).contains(2);
        assertThat(result.get(2)).contains(1);
        
        // Since all servers should be reachable, we should add more edges
        // Check that the graph is connected
        assertThat(isConnected(result, n)).isTrue();
    }

    @Test
    public void testWithMinimumServers() {
        int n = 2;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 2)
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size and keys
        assertThat(result).hasSize(n);
        
        // Verify connections
        assertThat(result.get(1)).contains(2);
        assertThat(result.get(2)).contains(1);
    }

    @Test
    public void testWithInvalidServerCount() {
        int n = 1; // Less than the minimum 2
        List<LogEntry> log = new ArrayList<>();
        
        assertThrows(IllegalArgumentException.class, () -> {
            networkReconstruction.reconstructNetwork(n, log);
        });
    }

    @Test
    public void testWithInvalidLogEntry() {
        int n = 3;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 4) // Server 4 doesn't exist
        );
        
        assertThrows(IllegalArgumentException.class, () -> {
            networkReconstruction.reconstructNetwork(n, log);
        });
    }

    @Test
    public void testWithDuplicateLogEntries() {
        int n = 3;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1000L, 1, 2),
            new LogEntry(1001L, 2, 1) // Same connection, different direction
        );
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify connections
        assertThat(result.get(1)).contains(2);
        assertThat(result.get(2)).contains(1);
        
        // Check the graph is connected
        assertThat(isConnected(result, n)).isTrue();
    }

    @Test
    public void testLargeNetwork() {
        int n = 20;
        List<LogEntry> log = new ArrayList<>();
        // Create a sparse network
        for (int i = 1; i < n; i++) {
            log.add(new LogEntry(1000L + i, i, i + 1));
        }
        
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Verify size
        assertThat(result).hasSize(n);
        
        // Check the graph is connected
        assertThat(isConnected(result, n)).isTrue();
        
        // Check average path length is optimized
        double avgPathLength = calculateAveragePathLength(result, n);
        double linearAvgPathLength = (n + 1) / 3.0; // Approximation for a linear network
        assertThat(avgPathLength).isLessThanOrEqualTo(linearAvgPathLength);
    }

    // Helper method to calculate average path length in a graph
    private double calculateAveragePathLength(Map<Integer, Set<Integer>> network, int n) {
        int totalPathLength = 0;
        int totalPaths = 0;
        
        // BFS from each node to find shortest paths
        for (int start = 1; start <= n; start++) {
            Queue<Integer> queue = new LinkedList<>();
            Map<Integer, Integer> distance = new HashMap<>();
            
            queue.add(start);
            distance.put(start, 0);
            
            while (!queue.isEmpty()) {
                int current = queue.poll();
                int currentDist = distance.get(current);
                
                for (int neighbor : network.get(current)) {
                    if (!distance.containsKey(neighbor)) {
                        distance.put(neighbor, currentDist + 1);
                        queue.add(neighbor);
                        totalPathLength += currentDist + 1;
                        totalPaths++;
                    }
                }
            }
        }
        
        return (double) totalPathLength / totalPaths;
    }
    
    // Helper method to check if a graph is connected
    private boolean isConnected(Map<Integer, Set<Integer>> network, int n) {
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        
        // Start BFS from node 1
        queue.add(1);
        visited.add(1);
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            
            for (int neighbor : network.get(current)) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.add(neighbor);
                }
            }
        }
        
        return visited.size() == n;
    }
}