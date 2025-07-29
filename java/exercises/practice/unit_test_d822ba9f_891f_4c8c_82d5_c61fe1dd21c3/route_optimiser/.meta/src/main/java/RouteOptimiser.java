import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

public class RouteOptimiser {

    private static class Edge {
        int target;
        int cost; // cost = timeWeight * time + tollWeight * toll

        Edge(int target, int cost) {
            this.target = target;
            this.cost = cost;
        }
    }

    public static List<Double> findOptimalRoutes(int N, List<int[]> edges, List<Integer> destinations, int timeWeight, int tollWeight) {
        // Build the graph as an adjacency list
        List<List<Edge>> graph = new ArrayList<>(N);
        for (int i = 0; i < N; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] e : edges) {
            int u = e[0];
            int v = e[1];
            int time = e[2];
            int toll = e[3];
            int cost = timeWeight * time + tollWeight * toll;
            graph.get(u).add(new Edge(v, cost));
        }

        // Dijkstra's algorithm initialization
        int[] dist = new int[N];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[0] = 0;
        PriorityQueue<int[]> queue = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));
        queue.offer(new int[] {0, 0}); // {node, cost}

        while (!queue.isEmpty()) {
            int[] curr = queue.poll();
            int node = curr[0];
            int curCost = curr[1];

            if (curCost > dist[node]) {
                continue;
            }

            for (Edge edge : graph.get(node)) {
                int nextNode = edge.target;
                int newCost = curCost + edge.cost;
                if (newCost < dist[nextNode]) {
                    dist[nextNode] = newCost;
                    queue.offer(new int[] {nextNode, newCost});
                }
            }
        }

        // Build the result list for each destination
        List<Double> results = new ArrayList<>();
        for (int dest : destinations) {
            if (dist[dest] == Integer.MAX_VALUE) {
                results.add(-1.0);
            } else {
                results.add((double) dist[dest]);
            }
        }

        return results;
    }
}