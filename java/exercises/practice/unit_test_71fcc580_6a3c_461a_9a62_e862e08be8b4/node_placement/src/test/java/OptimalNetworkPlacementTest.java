import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import java.util.*;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

public class OptimalNetworkPlacementTest {

    private OptimalNetworkPlacement optimizer;

    @BeforeEach
    public void setup() {
        optimizer = new OptimalNetworkPlacement();
    }

    @Test
    public void testSmallLineGraph() {
        // Line graph: 0 -- 1 -- 2 -- 3 -- 4
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 5; i++) {
            graph.put(i, new ArrayList<>());
        }
        addBidirectionalEdge(graph, 0, 1, 1.0);
        addBidirectionalEdge(graph, 1, 2, 1.0);
        addBidirectionalEdge(graph, 2, 3, 1.0);
        addBidirectionalEdge(graph, 3, 4, 1.0);

        List<Integer> result = optimizer.findOptimalPlacement(graph, 5, 1);
        
        // For K=1 in a line graph, the optimal placement is at the center
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEqualTo(2);
    }

    @Disabled("Remove to run test")
    @Test
    public void testStarGraph() {
        // Star graph with node 0 at center
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 6; i++) {
            graph.put(i, new ArrayList<>());
        }
        for (int i = 1; i < 6; i++) {
            addBidirectionalEdge(graph, 0, i, 1.0);
        }

        List<Integer> result = optimizer.findOptimalPlacement(graph, 6, 1);
        
        // For K=1 in a star graph, the optimal placement is at the center
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEqualTo(0);
    }

    @Disabled("Remove to run test")
    @Test
    public void testCompleteGraph() {
        // Complete graph where every node is connected to every other node
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 5; i++) {
            graph.put(i, new ArrayList<>());
            for (int j = 0; j < 5; j++) {
                if (i != j) {
                    graph.get(i).add(new Edge(j, 1.0));
                }
            }
        }

        List<Integer> result = optimizer.findOptimalPlacement(graph, 5, 1);
        
        // In a complete graph with equal weights, any node is optimal
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isBetween(0, 4);
    }

    @Disabled("Remove to run test")
    @Test
    public void testMultipleNodePlacement() {
        // Line graph: 0 -- 1 -- 2 -- 3 -- 4 -- 5 -- 6 -- 7 -- 8
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 9; i++) {
            graph.put(i, new ArrayList<>());
        }
        for (int i = 0; i < 8; i++) {
            addBidirectionalEdge(graph, i, i+1, 1.0);
        }

        List<Integer> result = optimizer.findOptimalPlacement(graph, 9, 3);
        
        // Optimal placement for K=3 would be at positions 2, 4, and 6 (evenly spaced)
        assertThat(result).hasSize(3);
        Collections.sort(result);
        assertThat(result).containsExactly(2, 4, 6);
    }

    @Disabled("Remove to run test")
    @Test
    public void testDisconnectedGraph() {
        // Two separate components
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 6; i++) {
            graph.put(i, new ArrayList<>());
        }
        // Component 1: 0 -- 1 -- 2
        addBidirectionalEdge(graph, 0, 1, 1.0);
        addBidirectionalEdge(graph, 1, 2, 1.0);
        
        // Component 2: 3 -- 4 -- 5
        addBidirectionalEdge(graph, 3, 4, 1.0);
        addBidirectionalEdge(graph, 4, 5, 1.0);

        List<Integer> result = optimizer.findOptimalPlacement(graph, 6, 2);
        
        // Optimal placement should put one node in each component
        assertThat(result).hasSize(2);
        Collections.sort(result);
        boolean validPlacement = 
            (result.contains(1) && result.contains(4)) ||
            (result.contains(0) && result.contains(4)) ||
            (result.contains(2) && result.contains(4)) ||
            (result.contains(1) && result.contains(3)) ||
            (result.contains(1) && result.contains(5));
        assertThat(validPlacement).isTrue();
    }

    @Disabled("Remove to run test")
    @Test
    public void testWeightedGraph() {
        // Graph with varying edge weights
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 4; i++) {
            graph.put(i, new ArrayList<>());
        }
        addBidirectionalEdge(graph, 0, 1, 1.0);
        addBidirectionalEdge(graph, 1, 2, 5.0);  // High latency link
        addBidirectionalEdge(graph, 2, 3, 1.0);
        addBidirectionalEdge(graph, 0, 3, 10.0); // Even higher latency link

        List<Integer> result = optimizer.findOptimalPlacement(graph, 4, 2);
        
        // Optimal placement should be one node on each side of the high latency link
        assertThat(result).hasSize(2);
        Collections.sort(result);
        assertThat(result).containsExactly(0, 3);
    }

    @Disabled("Remove to run test")
    @Test
    @Timeout(5) // 5 seconds timeout
    public void testLargeGraph() {
        // Create a larger graph to test performance
        Map<Integer, List<Edge>> graph = new HashMap<>();
        int size = 100;
        // Create a grid graph
        for (int i = 0; i < size; i++) {
            graph.put(i, new ArrayList<>());
        }
        
        // Connect in a grid pattern (10x10 grid)
        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < 10; j++) {
                int node = i * 10 + j;
                
                // Connect right
                if (j < 9) {
                    addBidirectionalEdge(graph, node, node + 1, 1.0);
                }
                
                // Connect down
                if (i < 9) {
                    addBidirectionalEdge(graph, node, node + 10, 1.0);
                }
            }
        }

        List<Integer> result = optimizer.findOptimalPlacement(graph, size, 4);
        
        // Just verify we get the right number of nodes and within time limit
        assertThat(result).hasSize(4);
        
        // Check all returned nodes are valid
        for (int node : result) {
            assertThat(node).isBetween(0, size - 1);
        }
        
        // Check for duplicates
        assertThat(new HashSet<>(result).size()).isEqualTo(result.size());
    }

    @Disabled("Remove to run test")
    @Test
    public void testK_EqualsNumNodes() {
        // Simple graph
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 5; i++) {
            graph.put(i, new ArrayList<>());
        }
        addBidirectionalEdge(graph, 0, 1, 1.0);
        addBidirectionalEdge(graph, 1, 2, 1.0);
        addBidirectionalEdge(graph, 2, 3, 1.0);
        addBidirectionalEdge(graph, 3, 4, 1.0);

        List<Integer> result = optimizer.findOptimalPlacement(graph, 5, 5);
        
        // If K equals the number of nodes, all nodes should be selected
        assertThat(result).hasSize(5);
        Collections.sort(result);
        assertThat(result).containsExactly(0, 1, 2, 3, 4);
    }

    @Disabled("Remove to run test")
    @Test
    public void testEmptyGraphEdgeCase() {
        Map<Integer, List<Edge>> graph = new HashMap<>();
        // Empty graph
        
        List<Integer> result = optimizer.findOptimalPlacement(graph, 0, 0);
        
        // Should handle empty graph without errors
        assertThat(result).isEmpty();
    }

    @Disabled("Remove to run test")
    @Test
    public void testComplexTopologyGraph() {
        // Create a more complex graph topology
        Map<Integer, List<Edge>> graph = new HashMap<>();
        for (int i = 0; i < 10; i++) {
            graph.put(i, new ArrayList<>());
        }
        
        // Ring topology with a central hub
        for (int i = 1; i < 10; i++) {
            addBidirectionalEdge(graph, 0, i, 1.0);  // Hub connections
            addBidirectionalEdge(graph, i, (i % 9) + 1, 2.0);  // Ring connections
        }
        
        List<Integer> result = optimizer.findOptimalPlacement(graph, 10, 2);
        
        // Hub should be one of the selected nodes
        assertThat(result).hasSize(2);
        assertThat(result).contains(0);
    }

    // Helper method to add edges in both directions
    private void addBidirectionalEdge(Map<Integer, List<Edge>> graph, int source, int destination, double latency) {
        graph.get(source).add(new Edge(destination, latency));
        graph.get(destination).add(new Edge(source, latency));
    }
}