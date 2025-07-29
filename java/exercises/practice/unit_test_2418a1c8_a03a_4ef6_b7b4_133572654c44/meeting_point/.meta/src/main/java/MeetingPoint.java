package meeting_point;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

public class MeetingPoint {

    public static int findOptimalMeetingPoint(int n, int[][] roads, int[] friends) {
        // Build the graph using an adjacency list
        List<Edge>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] road : roads) {
            int u = road[0];
            int v = road[1];
            int w = road[2];
            graph[u].add(new Edge(v, w));
            graph[v].add(new Edge(u, w));
        }

        // maxDistance[i] stores the maximum distance among all friends to node i
        int[] maxDistance = new int[n];
        // valid[i] is true if all friends can reach node i, otherwise false.
        boolean[] valid = new boolean[n];
        Arrays.fill(valid, true);

        // For each friend compute distances using Dijkstra's algorithm and update maxDistance.
        for (int friend : friends) {
            int[] dist = dijkstra(n, graph, friend);
            for (int i = 0; i < n; i++) {
                if (dist[i] == Integer.MAX_VALUE) {
                    valid[i] = false;
                } else {
                    maxDistance[i] = Math.max(maxDistance[i], dist[i]);
                }
            }
        }

        // Find the meeting point with the minimal maximum travel time.
        int result = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            if (valid[i]) {
                result = Math.min(result, maxDistance[i]);
            }
        }

        return result == Integer.MAX_VALUE ? -1 : result;
    }

    private static int[] dijkstra(int n, List<Edge>[] graph, int src) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[src] = 0;
        PriorityQueue<NodeDist> pq = new PriorityQueue<>(Comparator.comparingInt(nd -> nd.distance));
        pq.offer(new NodeDist(src, 0));

        while (!pq.isEmpty()) {
            NodeDist current = pq.poll();
            int u = current.node;
            int currentDist = current.distance;
            if (currentDist > dist[u]) {
                continue;
            }
            for (Edge edge : graph[u]) {
                int v = edge.target;
                int newDist = currentDist + edge.weight;
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    pq.offer(new NodeDist(v, newDist));
                }
            }
        }
        return dist;
    }

    private static class NodeDist {
        int node;
        int distance;

        NodeDist(int node, int distance) {
            this.node = node;
            this.distance = distance;
        }
    }

    private static class Edge {
        int target;
        int weight;

        Edge(int target, int weight) {
            this.target = target;
            this.weight = weight;
        }
    }
}