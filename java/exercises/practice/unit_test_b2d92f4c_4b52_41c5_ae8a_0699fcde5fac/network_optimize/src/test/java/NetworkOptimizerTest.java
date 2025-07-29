import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatExceptionOfType;

public class NetworkOptimizerTest {
    
    private NetworkOptimizer optimizer;
    
    @BeforeEach
    public void setUp() {
        optimizer = new NetworkOptimizer();
    }
    
    @Test
    public void testSmallNetworkWithNoSwaps() {
        // Line topology: 0 -- 1 -- 2 -- 3
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1));          // Node 0 connected to 1
        network.add(Arrays.asList(0, 2));       // Node 1 connected to 0 and 2
        network.add(Arrays.asList(1, 3));       // Node 2 connected to 1 and 3
        network.add(Arrays.asList(2));          // Node 3 connected to 2
        
        int result = optimizer.optimizeNetwork(network, 0);
        
        // Maximum latency in a line of 4 nodes is 3 hops (from node 0 to node 3)
        assertThat(result).isEqualTo(3);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testSmallNetworkWithOneSwap() {
        // Line topology: 0 -- 1 -- 2 -- 3
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1));          // Node 0 connected to 1
        network.add(Arrays.asList(0, 2));       // Node 1 connected to 0 and 2
        network.add(Arrays.asList(1, 3));       // Node 2 connected to 1 and 3
        network.add(Arrays.asList(2));          // Node 3 connected to 2
        
        int result = optimizer.optimizeNetwork(network, 1);
        
        // Optimal swap would add edge 0-3, creating a cycle, reducing max latency to 2
        assertThat(result).isEqualTo(2);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testStarTopology() {
        // Star topology: 0 is the central node connected to all others
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 2, 3, 4)); // Node 0 connected to all others
        network.add(Arrays.asList(0));          // Node 1 connected to 0
        network.add(Arrays.asList(0));          // Node 2 connected to 0
        network.add(Arrays.asList(0));          // Node 3 connected to 0
        network.add(Arrays.asList(0));          // Node 4 connected to 0
        
        int result = optimizer.optimizeNetwork(network, 0);
        
        // Maximum latency in a star is 2 (going through the central node)
        assertThat(result).isEqualTo(2);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testCompleteGraph() {
        // Complete graph - all nodes connected to all others
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 2, 3, 4)); // Node 0 connected to all others
        network.add(Arrays.asList(0, 2, 3, 4)); // Node 1 connected to all others
        network.add(Arrays.asList(0, 1, 3, 4)); // Node 2 connected to all others
        network.add(Arrays.asList(0, 1, 2, 4)); // Node 3 connected to all others
        network.add(Arrays.asList(0, 1, 2, 3)); // Node 4 connected to all others
        
        int result = optimizer.optimizeNetwork(network, 2);
        
        // Maximum latency in a complete graph is 1 (direct edge to any node)
        assertThat(result).isEqualTo(1);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testMediumSizedNetwork() {
        // Network with 7 nodes in a specific configuration
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 2));       // Node 0 connected to 1, 2
        network.add(Arrays.asList(0, 3));       // Node 1 connected to 0, 3
        network.add(Arrays.asList(0, 3, 4));    // Node 2 connected to 0, 3, 4
        network.add(Arrays.asList(1, 2, 5));    // Node 3 connected to 1, 2, 5
        network.add(Arrays.asList(2, 6));       // Node 4 connected to 2, 6
        network.add(Arrays.asList(3, 6));       // Node 5 connected to 3, 6
        network.add(Arrays.asList(4, 5));       // Node 6 connected to 4, 5
        
        int result = optimizer.optimizeNetwork(network, 1);
        
        // With one swap, we can reduce max latency from 4 to 3
        assertThat(result).isEqualTo(3);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testAlreadyOptimalNetwork() {
        // Ring topology with 5 nodes
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 4));       // Node 0 connected to 1, 4
        network.add(Arrays.asList(0, 2));       // Node 1 connected to 0, 2
        network.add(Arrays.asList(1, 3));       // Node 2 connected to 1, 3
        network.add(Arrays.asList(2, 4));       // Node 3 connected to 2, 4
        network.add(Arrays.asList(0, 3));       // Node 4 connected to 0, 3
        
        int result = optimizer.optimizeNetwork(network, 1);
        
        // This ring topology already has optimal latency (diameter 2), even with one swap
        assertThat(result).isEqualTo(2);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testComplexNetworkWithMultipleSwaps() {
        // A more complex network with 8 nodes
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 7));       // Node 0
        network.add(Arrays.asList(0, 2, 7));    // Node 1
        network.add(Arrays.asList(1, 3));       // Node 2
        network.add(Arrays.asList(2, 4, 5));    // Node 3
        network.add(Arrays.asList(3));          // Node 4
        network.add(Arrays.asList(3, 6));       // Node 5
        network.add(Arrays.asList(5, 7));       // Node 6
        network.add(Arrays.asList(0, 1, 6));    // Node 7
        
        int result = optimizer.optimizeNetwork(network, 2);
        
        // With two strategic swaps, we can reduce the maximum latency
        assertThat(result).isEqualTo(3);
    }
    
    @Disabled("Remove to run test")
    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testLargeNetworkPerformance() {
        // Generate a large network (path topology with 30 nodes)
        List<List<Integer>> network = new ArrayList<>();
        for (int i = 0; i < 30; i++) {
            List<Integer> connections = new ArrayList<>();
            if (i > 0) connections.add(i - 1);
            if (i < 29) connections.add(i + 1);
            network.add(connections);
        }
        
        int result = optimizer.optimizeNetwork(network, 5);
        
        // With 5 well-placed swaps, we can reduce the maximum latency significantly
        assertThat(result).isLessThan(29); // Original max latency is 29 (end to end)
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testKLargerThanPossibleSwaps() {
        // Small complete graph - no more optimizations possible
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1, 2));       // Node 0 connected to all others
        network.add(Arrays.asList(0, 2));       // Node 1 connected to all others
        network.add(Arrays.asList(0, 1));       // Node 2 connected to all others
        
        int result = optimizer.optimizeNetwork(network, 10);
        
        // Already a complete graph, maximum latency is 1
        assertThat(result).isEqualTo(1);
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testInvalidInput() {
        // Empty network
        List<List<Integer>> emptyNetwork = new ArrayList<>();
        
        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> optimizer.optimizeNetwork(emptyNetwork, 1))
                .withMessage("Network cannot be empty");
        
        // Negative K
        List<List<Integer>> validNetwork = new ArrayList<>();
        validNetwork.add(Arrays.asList(1));
        validNetwork.add(Arrays.asList(0));
        
        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> optimizer.optimizeNetwork(validNetwork, -1))
                .withMessage("Number of allowed swaps cannot be negative");
    }
    
    @Disabled("Remove to run test")
    @Test
    public void testDisconnectedNetwork() {
        // Two disconnected components
        List<List<Integer>> network = new ArrayList<>();
        network.add(Arrays.asList(1));          // Node 0 connected to 1
        network.add(Arrays.asList(0));          // Node 1 connected to 0
        network.add(Arrays.asList(3));          // Node 2 connected to 3
        network.add(Arrays.asList(2));          // Node 3 connected to 2
        
        assertThatExceptionOfType(IllegalArgumentException.class)
                .isThrownBy(() -> optimizer.optimizeNetwork(network, 0))
                .withMessage("Initial network must be connected");
        
        // With one swap, we can connect the two components
        int result = optimizer.optimizeNetwork(network, 1);
        assertThat(result).isEqualTo(3); // After connecting, max distance is 3
    }
}