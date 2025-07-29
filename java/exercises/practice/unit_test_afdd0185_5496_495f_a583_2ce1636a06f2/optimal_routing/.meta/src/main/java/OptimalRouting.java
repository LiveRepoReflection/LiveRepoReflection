import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

public class OptimalRouting {

    private int n;
    private List<Edge>[] graph;

    /**
     * Initialize the network with n nodes (0 to n-1).
     * @param n the number of nodes in the network.
     */
    public synchronized void initialize(int n) {
        this.n = n;
        graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
    }

    /**
     * Adds a bidirectional link between node1 and node2 with the specified latency.
     * If the link already exists, update its latency.
     * The congestion factor is set to 1 initially.
     * @param node1 first node.
     * @param node2 second node.
     * @param latency the base latency of the link.
     */
    public synchronized void addLink(int node1, int node2, int latency) {
        Edge edge1 = findEdge(node1, node2);
        if (edge1 != null) {
            edge1.latency = latency;
        } else {
            graph[node1].add(new Edge(node2, latency, 1));
        }
        
        Edge edge2 = findEdge(node2, node1);
        if (edge2 != null) {
            edge2.latency = latency;
        } else {
            graph[node2].add(new Edge(node1, latency, 1));
        }
    }

    /**
     * Removes the bidirectional link between node1 and node2, if it exists.
     * @param node1 first node.
     * @param node2 second node.
     */
    public synchronized void removeLink(int node1, int node2) {
        Edge edge1 = findEdge(node1, node2);
        if (edge1 != null) {
            graph[node1].remove(edge1);
        }
        Edge edge2 = findEdge(node2, node1);
        if (edge2 != null) {
            graph[node2].remove(edge2);
        }
    }

    /**
     * Updates the latency of the bidirectional link between node1 and node2.
     * @param node1 first node.
     * @param node2 second node.
     * @param latency the new latency.
     */
    public synchronized void updateLatency(int node1, int node2, int latency) {
        Edge edge1 = findEdge(node1, node2);
        if (edge1 != null) {
            edge1.latency = latency;
        }
        Edge edge2 = findEdge(node2, node1);
        if (edge2 != null) {
            edge2.latency = latency;
        }
    }

    /**
     * Updates the congestion factor of the bidirectional link between node1 and node2.
     * @param node1 first node.
     * @param node2 second node.
     * @param congestionFactor new congestion factor (>=1).
     */
    public synchronized void updateCongestion(int node1, int node2, int congestionFactor) {
        Edge edge1 = findEdge(node1, node2);
        if (edge1 != null) {
            edge1.congestion = congestionFactor;
        }
        Edge edge2 = findEdge(node2, node1);
        if (edge2 != null) {
            edge2.congestion = congestionFactor;
        }
    }

    /**
     * Retrieves the effective latency (latency * congestion factor) of the link between node1 and node2.
     * If the link does not exist, returns 0.
     * @param node1 first node.
     * @param node2 second node.
     * @return effective latency of the link.
     */
    public synchronized int getEffectiveLatency(int node1, int node2) {
        Edge edge = findEdge(node1, node2);
        if (edge != null) {
            return edge.latency * edge.congestion;
        }
        return 0;
    }

    /**
     * Finds the optimal (minimum effective latency) path between source and destination using Dijkstra's algorithm.
     * If no path exists, returns an empty list.
     * @param source starting node.
     * @param destination target node.
     * @return list of nodes representing the optimal path.
     */
    public synchronized List<Integer> findOptimalPath(int source, int destination) {
        // Distance array: use a large value to denote infinity.
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;

        // Previous node tracker for path reconstruction.
        int[] prev = new int[n];
        Arrays.fill(prev, -1);

        // Priority queue for Dijkstra: each element is a pair (node, current distance).
        PriorityQueue<NodeCost> pq = new PriorityQueue<>();
        pq.offer(new NodeCost(source, 0));

        boolean[] visited = new boolean[n];

        while (!pq.isEmpty()) {
            NodeCost current = pq.poll();
            int u = current.node;
            if (visited[u]) {
                continue;
            }
            visited[u] = true;
            if (u == destination) {
                break;
            }
            for (Edge edge : graph[u]) {
                int v = edge.to;
                int weight = edge.latency * edge.congestion;
                if (dist[u] != Integer.MAX_VALUE && dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    prev[v] = u;
                    pq.offer(new NodeCost(v, dist[v]));
                }
            }
        }

        // If destination is unreachable, return empty list.
        if (dist[destination] == Integer.MAX_VALUE) {
            return new ArrayList<>();
        }

        // Reconstruct the path from destination back to source.
        List<Integer> path = new ArrayList<>();
        for (int at = destination; at != -1; at = prev[at]) {
            path.add(0, at);
        }
        return path;
    }

    /**
     * Finds an edge in the adjacency list from node u to node v.
     * Returns null if no such edge exists.
     */
    private Edge findEdge(int u, int v) {
        for (Edge e : graph[u]) {
            if (e.to == v) {
                return e;
            }
        }
        return null;
    }

    /**
     * Inner class to represent an edge in the network.
     */
    private static class Edge {
        int to;
        int latency;
        int congestion;

        Edge(int to, int latency, int congestion) {
            this.to = to;
            this.latency = latency;
            this.congestion = congestion;
        }
    }

    /**
     * Inner class for Dijkstra's priority queue.
     */
    private static class NodeCost implements Comparable<NodeCost> {
        int node;
        int cost;

        NodeCost(int node, int cost) {
            this.node = node;
            this.cost = cost;
        }

        @Override
        public int compareTo(NodeCost other) {
            return Integer.compare(this.cost, other.cost);
        }
    }
}