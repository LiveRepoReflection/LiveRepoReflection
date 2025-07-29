package network_towers;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.PriorityQueue;

public class NetworkTowersTest {

    // Helper: computes the shortest distances from a source node using Dijkstra's algorithm.
    private Map<Integer, Integer> dijkstra(int source, Map<Integer, List<int[]>> graph, int N) {
        Map<Integer, Integer> minDist = new HashMap<>();
        for (int i = 0; i < N; i++) {
            minDist.put(i, Integer.MAX_VALUE);
        }
        minDist.put(source, 0);
        PriorityQueue<int[]> heap = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));
        heap.offer(new int[]{source, 0});
        while (!heap.isEmpty()) {
            int[] cur = heap.poll();
            int node = cur[0], dist = cur[1];
            if (dist > minDist.get(node)) {
                continue;
            }
            if (!graph.containsKey(node)) {
                continue;
            }
            for (int[] edge : graph.get(node)) {
                int neighbor = edge[0];
                int weight = edge[1];
                int newDist = dist + weight;
                if (newDist < minDist.get(neighbor)) {
                    minDist.put(neighbor, newDist);
                    heap.offer(new int[]{neighbor, newDist});
                }
            }
        }
        return minDist;
    }

    // Helper: builds a graph from a list of edges. Each edge is in format [u, v, cost].
    private Map<Integer, List<int[]>> buildGraph(int N, List<int[]> edges) {
        Map<Integer, List<int[]>> graph = new HashMap<>();
        for (int i = 0; i < N; i++) {
            graph.put(i, new ArrayList<>());
        }
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int cost = edge[2];
            graph.get(u).add(new int[]{v, cost});
            graph.get(v).add(new int[]{u, cost});
        }
        return graph;
    }

    // Helper: computes the total coverage given a set of tower placements.
    // Direct coverage: each city with a tower.
    // Indirect coverage: a city without a tower is covered if it has at least K towers within distance D.
    private int computeCoverage(Set<Integer> towers, int N, List<int[]> edges, int D, int K) {
        int coverage = towers.size(); // direct coverage

        Map<Integer, List<int[]>> graph = buildGraph(N, edges);

        for (int city = 0; city < N; city++) {
            if (towers.contains(city)) {
                continue;
            }
            int count = 0;
            for (int tower : towers) {
                Map<Integer, Integer> distMap = dijkstra(tower, graph, N);
                if (distMap.get(city) <= D) {
                    count++;
                }
                if (count >= K) {
                    break;
                }
            }
            if (count >= K) {
                coverage++;
            }
        }
        return coverage;
    }

    // Test when graph is empty.
    @Test
    public void testEmptyGraph() {
        int N = 0;
        List<int[]> edges = new ArrayList<>();
        int B = 10;
        int D = 5;
        int K = 1;
        int tower_cost = 3;

        Set<Integer> result = NetworkTowers.findOptimalTowers(N, edges, B, D, K, tower_cost);
        assertNotNull(result);
        assertEquals(0, result.size());
    }

    // Test when budget is insufficient to build any towers.
    @Test
    public void testNoTowersWithinBudget() {
        int N = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 2},
            new int[]{1, 2, 3},
            new int[]{2, 3, 2},
            new int[]{3, 4, 1}
        );
        int B = 2; // Budget less than tower_cost.
        int D = 5;
        int K = 1;
        int tower_cost = 3;

        Set<Integer> result = NetworkTowers.findOptimalTowers(N, edges, B, D, K, tower_cost);
        // Expecting no towers can be built so coverage is 0.
        assertNotNull(result);
        assertTrue(result.isEmpty());
    }

    // Test with a small graph using the example provided in the problem description.
    @Test
    public void testSmallGraphExample() {
        int N = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1},
            new int[]{0, 2, 4},
            new int[]{1, 2, 2},
            new int[]{1, 3, 5},
            new int[]{2, 4, 1},
            new int[]{3, 4, 3}
        );
        int B = 10;
        int D = 4;
        int K = 2;
        int tower_cost = 3;

        Set<Integer> result = NetworkTowers.findOptimalTowers(N, edges, B, D, K, tower_cost);
        // Validate that the total cost does not exceed the budget.
        assertNotNull(result);
        assertTrue(result.size() * tower_cost <= B);

        // Compute coverage of the returned solution.
        int coverage = computeCoverage(result, N, edges, D, K);
        // From the example, the best achievable coverage is 4.
        assertTrue(coverage >= 4, "Expected coverage to be at least 4, but was " + coverage);
    }

    // Test with a disconnected graph.
    @Test
    public void testDisconnectedGraph() {
        int N = 6;
        List<int[]> edges = Arrays.asList(
            // Component 1: nodes 0,1,2
            new int[]{0, 1, 2},
            new int[]{1, 2, 2},
            // Component 2: nodes 3,4,5
            new int[]{3, 4, 3},
            new int[]{4, 5, 3}
        );
        int B = 12;
        int D = 4;
        int K = 1;
        int tower_cost = 4;

        Set<Integer> result = NetworkTowers.findOptimalTowers(N, edges, B, D, K, tower_cost);
        assertNotNull(result);
        // Cost constraint
        assertTrue(result.size() * tower_cost <= B);
        
        // Compute coverage: in a disconnected graph, expect that if towers are placed it covers each component separately.
        int coverage = computeCoverage(result, N, edges, D, K);
        // Maximum possible coverage is 6 if towers are well placed.
        assertTrue(coverage >= 3, "Expected coverage to be at least 3, but was " + coverage);
    }

    // Test with a case where the budget allows towers on all cities.
    @Test
    public void testAllCitiesHaveTowers() {
        int N = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1},
            new int[]{1, 2, 1},
            new int[]{2, 3, 1},
            new int[]{3, 0, 1}
        );
        int B = 20;
        int D = 2;
        int K = 1;
        int tower_cost = 3;

        Set<Integer> result = NetworkTowers.findOptimalTowers(N, edges, B, D, K, tower_cost);
        // Since budget is ample, it's possible to cover all nodes directly.
        assertNotNull(result);
        // It is acceptable if not all towers are built, but coverage should be maximal.
        int coverage = computeCoverage(result, N, edges, D, K);
        assertEquals(N, coverage, "Expected all cities to be covered, but coverage was " + coverage);
    }
}