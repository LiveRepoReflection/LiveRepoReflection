import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

class DynamicDijkstraTest {
    private DynamicDijkstra solver;

    @BeforeEach
    void setUp() {
        solver = new DynamicDijkstra();
    }

    @Test
    void testBasicGraph() {
        // Simple graph with 4 nodes
        int[][] edges = {
            {0, 1, 1},
            {1, 2, 2},
            {2, 3, 3},
            {0, 3, 10}
        };
        solver.initialize(4, edges);
        solver.setSources(List.of(0));
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 1, 3, 6);
    }

    @Test
    void testMultipleSources() {
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 3},
            {2, 3, 1},
            {3, 4, 2},
            {0, 4, 15}
        };
        solver.initialize(5, edges);
        solver.setSources(List.of(0, 2));
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 5, 0, 1, 3);
    }

    @Test
    void testDisconnectedGraph() {
        int[][] edges = {
            {0, 1, 1},
            {1, 2, 1},
            {3, 4, 1}
        };
        solver.initialize(5, edges);
        solver.setSources(List.of(0));
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 1, 2, Integer.MAX_VALUE, Integer.MAX_VALUE);
    }

    @Test
    void testEdgeUpdates() {
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5},
            {0, 2, 15}
        };
        solver.initialize(3, edges);
        solver.setSources(List.of(0));
        
        // Initial shortest paths
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 5, 10);

        // Update edge weight and verify new shortest paths
        solver.updateEdge(0, 2, 8);
        distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 5, 8);
    }

    @Test
    void testLargeGraph() {
        // Create a larger graph to test performance
        int n = 1000;
        List<int[]> edges = new ArrayList<>();
        
        // Create a connected graph
        for (int i = 0; i < n-1; i++) {
            edges.add(new int[]{i, i+1, i+1});
            if (i < n-2) {
                edges.add(new int[]{i, i+2, i+2});
            }
        }

        solver.initialize(n, edges.toArray(new int[0][]));
        solver.setSources(List.of(0));
        
        // Test multiple updates
        for (int i = 0; i < 100; i++) {
            solver.updateEdge(i, i+1, i*2);
        }
        
        int[] distances = solver.getShortestPaths();
        assertThat(distances[n-1]).isGreaterThan(0);
        assertThat(distances[n-1]).isLessThan(Integer.MAX_VALUE);
    }

    @Test
    void testZeroWeightEdges() {
        int[][] edges = {
            {0, 1, 1},
            {1, 2, 0},
            {2, 3, 1}
        };
        solver.initialize(4, edges);
        solver.setSources(List.of(0));
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 1, 1, 2);
    }

    @Test
    void testCyclicGraph() {
        int[][] edges = {
            {0, 1, 1},
            {1, 2, 2},
            {2, 0, 3}
        };
        solver.initialize(3, edges);
        solver.setSources(List.of(0));
        int[] distances = solver.getShortestPaths();
        assertThat(distances).containsExactly(0, 1, 3);
    }

    @Test
    void testFrequentUpdates() {
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5},
            {2, 3, 5},
            {3, 4, 5}
        };
        solver.initialize(5, edges);
        solver.setSources(List.of(0));

        // Perform multiple updates and verify correctness
        for (int i = 1; i <= 100; i++) {
            solver.updateEdge(0, 1, i % 10 + 1);
            int[] distances = solver.getShortestPaths();
            assertThat(distances[1]).isEqualTo(i % 10 + 1);
        }
    }

    @Test
    void testSourceUpdates() {
        int[][] edges = {
            {0, 1, 1},
            {1, 2, 2},
            {2, 3, 3}
        };
        solver.initialize(4, edges);
        
        // Test with different source combinations
        solver.setSources(List.of(0));
        int[] distances1 = solver.getShortestPaths();
        
        solver.setSources(List.of(1));
        int[] distances2 = solver.getShortestPaths();
        
        solver.setSources(List.of(0, 2));
        int[] distances3 = solver.getShortestPaths();

        assertThat(distances1).containsExactly(0, 1, 3, 6);
        assertThat(distances2).containsExactly(Integer.MAX_VALUE, 0, 2, 5);
        assertThat(distances3).containsExactly(0, 1, 0, 3);
    }
}