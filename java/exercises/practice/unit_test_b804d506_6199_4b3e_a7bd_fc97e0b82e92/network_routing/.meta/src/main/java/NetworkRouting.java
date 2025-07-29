import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

public class NetworkRouting {
    private final int n;
    private final List<Edge>[] graph;

    @SuppressWarnings("unchecked")
    public NetworkRouting(int n) {
        this.n = n;
        graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
    }
    
    public void addConnection(int u, int v, int latency) {
        if (u < 0 || u >= n || v < 0 || v >= n || latency <= 0) {
            throw new IllegalArgumentException("Invalid arguments for addConnection");
        }
        graph[u].add(new Edge(v, latency));
    }
    
    public void removeConnection(int u, int v, int latency) {
        if (u < 0 || u >= n || v < 0 || v >= n || latency <= 0) {
            throw new IllegalArgumentException("Invalid arguments for removeConnection");
        }
        List<Edge> edges = graph[u];
        for (int i = 0; i < edges.size(); i++) {
            Edge edge = edges.get(i);
            if (edge.v == v && edge.latency == latency) {
                edges.remove(i);
                break;
            }
        }
    }
    
    public int findKthSmallestPath(int start, int end, int k) {
        if (start < 0 || start >= n || end < 0 || end >= n || k < 1) {
            throw new IllegalArgumentException("Invalid arguments for findKthSmallestPath");
        }
        // count[i] stores number of times node i is popped from the queue, i.e., number of paths reaching i.
        int[] count = new int[n];
        // PriorityQueue for paths: (totalCost, currentNode)
        PriorityQueue<Path> pq = new PriorityQueue<>((a, b) -> a.cost - b.cost);
        pq.offer(new Path(start, 0));
        
        while (!pq.isEmpty()) {
            Path current = pq.poll();
            int node = current.node;
            int cost = current.cost;
            count[node]++;
            // If destination reached, and this is the kth occurrence, return cost.
            if (node == end && count[node] == k) {
                return cost;
            }
            // Expand this node only if we haven't exceeded k expansions for it.
            if (count[node] <= k) {
                for (Edge edge : graph[node]) {
                    pq.offer(new Path(edge.v, cost + edge.latency));
                }
            }
        }
        return -1;
    }
    
    // Inner class for priority queue entries representing a path ending at a node with cumulative cost.
    private static class Path {
        int node;
        int cost;
        
        Path(int node, int cost) {
            this.node = node;
            this.cost = cost;
        }
    }
    
    // Inner class representing a directed edge in the network.
    private static class Edge {
        int v;
        int latency;
        
        Edge(int v, int latency) {
            this.v = v;
            this.latency = latency;
        }
    }
}