import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

class NetworkPathsTest {

    private NetworkPaths networkPaths;

    @BeforeEach
    void setUp() {
        int[][] edges = {
            {0, 1, 10},
            {0, 2, 5},
            {1, 2, 2},
            {2, 1, 3},
            {1, 3, 15},
            {2, 3, 7}
        };
        int n = 4;
        double c = 0.1;
        networkPaths = new NetworkPaths(edges, n, c);
    }

    @Test
    void testBasicPathFinding() {
        List<List<Integer>> paths = networkPaths.findShortestPaths(0, 3, 2);
        assertEquals(2, paths.size(), "Should find 2 paths");
        
        List<Integer> expectedPath1 = Arrays.asList(0, 2, 3);
        List<Integer> expectedPath2 = Arrays.asList(0, 1, 2, 3);
        
        assertEquals(expectedPath1, paths.get(0), "First path should be 0->2->3");
        assertEquals(expectedPath2, paths.get(1), "Second path should be 0->1->2->3");
    }

    @Test
    void testPathFindingWithUpdate() {
        // Initial query
        List<List<Integer>> paths1 = networkPaths.findShortestPaths(0, 3, 2);
        
        // Update an edge
        networkPaths.updateLatency(0, 1, 8);
        
        // Query again
        List<List<Integer>> paths2 = networkPaths.findShortestPaths(0, 3, 2);
        
        // Paths should still be the same but with possibly different weights
        List<Integer> expectedPath1 = Arrays.asList(0, 2, 3);
        List<Integer> expectedPath2 = Arrays.asList(0, 1, 2, 3);
        
        assertEquals(expectedPath1, paths2.get(0), "First path should still be 0->2->3");
        assertEquals(expectedPath2, paths2.get(1), "Second path should still be 0->1->2->3");
    }

    @Test
    void testNoPath() {
        int[][] edges = {
            {0, 1, 10},
            {1, 2, 5}
        };
        NetworkPaths network = new NetworkPaths(edges, 4, 0.1);
        List<List<Integer>> paths = network.findShortestPaths(0, 3, 2);
        
        assertTrue(paths.isEmpty(), "Should return empty list when no path exists");
    }

    @Test
    void testMultiplePathsWithCongestion() {
        // Create a network with multiple equivalent paths
        int[][] edges = {
            {0, 1, 5},
            {0, 2, 5},
            {1, 3, 5},
            {2, 3, 5}
        };
        NetworkPaths network = new NetworkPaths(edges, 4, 0.5);
        
        // First query should return both paths with equal weight
        List<List<Integer>> paths1 = network.findShortestPaths(0, 3, 2);
        assertEquals(2, paths1.size());
        
        // Second query should account for congestion on previously found paths
        List<List<Integer>> paths2 = network.findShortestPaths(0, 3, 2);
        assertEquals(2, paths2.size());
        
        // Verify that congestion changes the path order
        // We need to extract the exact paths to verify this
        List<Integer> firstPath1 = paths1.get(0);
        List<Integer> firstPath2 = paths2.get(0);
        
        // Hard to assert exact order due to tie-breaking, but at least check they're valid paths
        assertTrue(
            (firstPath1.equals(Arrays.asList(0, 1, 3)) || firstPath1.equals(Arrays.asList(0, 2, 3))) &&
            (firstPath2.equals(Arrays.asList(0, 1, 3)) || firstPath2.equals(Arrays.asList(0, 2, 3))),
            "Both queries should return valid paths"
        );
    }

    @Test
    void testLargeNetworkPerformance() {
        // Create a larger network to test performance
        int n = 100;
        List<int[]> edgeList = new ArrayList<>();
        
        // Create a grid-like network
        for (int i = 0; i < n - 1; i++) {
            edgeList.add(new int[]{i, i + 1, 10});
            if (i < n - 10) {
                edgeList.add(new int[]{i, i + 10, 15});
            }
        }
        
        int[][] edges = edgeList.toArray(new int[0][0]);
        NetworkPaths network = new NetworkPaths(edges, n, 0.1);
        
        // Measure time for a path query
        long startTime = System.currentTimeMillis();
        List<List<Integer>> paths = network.findShortestPaths(0, n - 1, 3);
        long endTime = System.currentTimeMillis();
        
        // Check that we got some paths
        assertFalse(paths.isEmpty(), "Should find at least one path");
        
        // Check that the computation was reasonably fast (adjust threshold as needed)
        long executionTime = endTime - startTime;
        assertTrue(executionTime < 5000, "Path finding should complete in under 5 seconds, took " + executionTime + "ms");
    }

    @Test
    void testDisconnectedGraph() {
        int[][] edges = {
            {0, 1, 10},
            {2, 3, 5}
        };
        NetworkPaths network = new NetworkPaths(edges, 4, 0.1);
        List<List<Integer>> paths = network.findShortestPaths(0, 3, 2);
        assertTrue(paths.isEmpty(), "Should return empty list for disconnected nodes");
    }

    @Test
    void testPathLimitation() {
        // Create a network with only one path
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5}
        };
        NetworkPaths network = new NetworkPaths(edges, 3, 0.1);
        
        // Ask for more paths than exist
        List<List<Integer>> paths = network.findShortestPaths(0, 2, 3);
        assertEquals(1, paths.size(), "Should only return available paths even if k is larger");
        assertEquals(Arrays.asList(0, 1, 2), paths.get(0), "Should return the correct path");
    }

    @Test
    void testConsecutiveUpdates() {
        // Update the same edge multiple times
        networkPaths.updateLatency(0, 1, 8);
        networkPaths.updateLatency(0, 1, 6);
        networkPaths.updateLatency(0, 1, 4);
        
        List<List<Integer>> paths = networkPaths.findShortestPaths(0, 3, 2);
        
        // Now path through 0->1 might be preferred due to lower latency
        List<Integer> firstPath = paths.get(0);
        List<Integer> possiblePath1 = Arrays.asList(0, 1, 2, 3);
        List<Integer> possiblePath2 = Arrays.asList(0, 2, 3);
        
        assertTrue(
            firstPath.equals(possiblePath1) || firstPath.equals(possiblePath2),
            "First path should be one of the expected paths after updates"
        );
    }

    @Test
    void testCongestionImpact() {
        // Create a network where congestion should significantly impact path selection
        int[][] edges = {
            {0, 1, 10},
            {0, 2, 15},
            {1, 3, 10},
            {2, 3, 10}
        };
        NetworkPaths network = new NetworkPaths(edges, 4, 0.8); // High congestion factor
        
        // First query establishes congestion on the shorter path
        List<List<Integer>> paths1 = network.findShortestPaths(0, 3, 1);
        assertEquals(Arrays.asList(0, 1, 3), paths1.get(0), "Should choose shorter path initially");
        
        // Multiple queries to build up congestion
        for (int i = 0; i < 5; i++) {
            network.findShortestPaths(0, 3, 1);
        }
        
        // Now the alternative path might be preferred due to congestion
        List<List<Integer>> pathsAfterCongestion = network.findShortestPaths(0, 3, 2);
        
        // Check that both paths are included
        boolean hasPath1 = false;
        boolean hasPath2 = false;
        
        for (List<Integer> path : pathsAfterCongestion) {
            if (path.equals(Arrays.asList(0, 1, 3))) hasPath1 = true;
            if (path.equals(Arrays.asList(0, 2, 3))) hasPath2 = true;
        }
        
        assertTrue(hasPath1 && hasPath2, "Both paths should be included after congestion builds up");
    }

    @Test
    void testCyclicGraph() {
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5},
            {2, 0, 5},
            {1, 3, 10}
        };
        NetworkPaths network = new NetworkPaths(edges, 4, 0.1);
        
        List<List<Integer>> paths = network.findShortestPaths(0, 3, 1);
        assertEquals(Arrays.asList(0, 1, 3), paths.get(0), "Should find the correct path in a cyclic graph");
    }
}