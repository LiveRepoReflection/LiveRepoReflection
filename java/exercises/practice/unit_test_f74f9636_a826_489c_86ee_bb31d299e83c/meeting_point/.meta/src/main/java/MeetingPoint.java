import java.util.*;

public class MeetingPoint {
    public int findOptimalMeetingPoint(int n, int[][] edges, int[] employeeLocations, int maxTravelTime) {
        if (n <= 0) {
            return -1;
        }
        // Validate employee locations.
        for (int loc : employeeLocations) {
            if (loc < 0 || loc >= n) {
                throw new IllegalArgumentException("Invalid employee location: " + loc);
            }
        }
        
        // Build graph as an adjacency list.
        List<int[]>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            if (edge.length != 3) {
                continue;
            }
            int u = edge[0], v = edge[1], w = edge[2];
            if (u < 0 || u >= n || v < 0 || v >= n) {
                continue;
            }
            graph[u].add(new int[]{v, w});
            graph[v].add(new int[]{u, w});
        }
        
        // Initialize total distances for each building and candidate validity.
        long[] totalDistances = new long[n];
        boolean[] validCandidate = new boolean[n];
        Arrays.fill(validCandidate, true);
        
        // For each employee, compute shortest paths using Dijkstra.
        for (int employee : employeeLocations) {
            int[] distances = dijkstra(n, graph, employee);
            for (int i = 0; i < n; i++) {
                if (distances[i] == Integer.MAX_VALUE / 2) {
                    validCandidate[i] = false;
                } else {
                    totalDistances[i] += distances[i];
                }
            }
        }
        
        // Select optimal meeting point.
        int optimalBuilding = -1;
        long minTotal = Long.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            if (!validCandidate[i]) {
                continue;
            }
            if (totalDistances[i] < minTotal) {
                minTotal = totalDistances[i];
                optimalBuilding = i;
            }
        }
        
        if (optimalBuilding == -1 || minTotal > maxTravelTime) {
            return -1;
        }
        return optimalBuilding;
    }
    
    private int[] dijkstra(int n, List<int[]>[] graph, int source) {
        int INF = Integer.MAX_VALUE / 2;
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        dist[source] = 0;
        
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a.distance));
        pq.add(new Node(source, 0));
        
        while (!pq.isEmpty()) {
            Node curr = pq.poll();
            int u = curr.node;
            if (curr.distance != dist[u]) {
                continue;
            }
            for (int[] neighbor : graph[u]) {
                int v = neighbor[0];
                int weight = neighbor[1];
                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    pq.add(new Node(v, dist[v]));
                }
            }
        }
        return dist;
    }
    
    private static class Node {
        int node;
        int distance;
        
        public Node(int node, int distance) {
            this.node = node;
            this.distance = distance;
        }
    }
}