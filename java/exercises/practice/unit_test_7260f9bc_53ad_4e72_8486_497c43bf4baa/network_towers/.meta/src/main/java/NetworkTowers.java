package network_towers;

import java.util.*;

public class NetworkTowers {

    public static Set<Integer> findOptimalTowers(int N, List<int[]> edges, int B, int D, int K, int tower_cost) {
        Map<Integer, List<int[]>> graph = buildGraph(N, edges);
        int maxTowerCount = B / tower_cost;
        Set<Integer> towers = new HashSet<>();
        int currentCoverage = computeCoverage(towers, N, graph, D, K);

        // Greedy selection of towers: iteratively add the tower that provides maximum marginal coverage.
        for (int i = 0; i < maxTowerCount; i++) {
            int bestCandidate = -1;
            int bestIncrease = 0;

            for (int city = 0; city < N; city++) {
                if (towers.contains(city)) {
                    continue;
                }
                Set<Integer> newTowers = new HashSet<>(towers);
                newTowers.add(city);
                int newCoverage = computeCoverage(newTowers, N, graph, D, K);
                int increase = newCoverage - currentCoverage;
                if (increase > bestIncrease) {
                    bestIncrease = increase;
                    bestCandidate = city;
                }
            }

            if (bestCandidate == -1 || bestIncrease <= 0) {
                break;
            }

            towers.add(bestCandidate);
            currentCoverage = computeCoverage(towers, N, graph, D, K);
        }
        return towers;
    }

    // Builds the graph from a list of edges.
    private static Map<Integer, List<int[]>> buildGraph(int N, List<int[]> edges) {
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

    // Dijkstra's algorithm to compute shortest distances from source to all other nodes.
    private static int[] dijkstra(int source, int N, Map<Integer, List<int[]>> graph) {
        int[] dist = new int[N];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));
        pq.offer(new int[]{source, 0});

        while (!pq.isEmpty()) {
            int[] current = pq.poll();
            int node = current[0];
            int distance = current[1];

            if (distance > dist[node]) {
                continue;
            }

            List<int[]> neighbors = graph.get(node);
            if (neighbors == null) {
                continue;
            }

            for (int[] neighborInfo : neighbors) {
                int neighbor = neighborInfo[0];
                int weight = neighborInfo[1];
                int newDist = dist[node] + weight;
                if (newDist < dist[neighbor]) {
                    dist[neighbor] = newDist;
                    pq.offer(new int[]{neighbor, newDist});
                }
            }
        }
        return dist;
    }

    // Computes total coverage given tower placements.
    // Direct coverage: a city with a tower.
    // Indirect coverage: a city without a tower is covered if at least K towers are within distance D.
    private static int computeCoverage(Set<Integer> towers, int N, Map<Integer, List<int[]>> graph, int D, int K) {
        int coverage = towers.size(); // Directly covered cities.
        for (int city = 0; city < N; city++) {
            if (towers.contains(city)) {
                continue;
            }
            int count = 0;
            for (int tower : towers) {
                int[] distances = dijkstra(tower, N, graph);
                if (distances[city] <= D) {
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
}