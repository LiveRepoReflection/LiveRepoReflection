import java.util.*;

public class OptimalPaths {
    /**
     * Finds the shortest path from any source node to the target node, respecting capacity constraints.
     *
     * @param n       The number of nodes in the graph.
     * @param edges   A list of edges, each represented as [u, v, weight, capacity].
     * @param sources A list of source nodes.
     * @param target  The target node.
     * @return The shortest distance from any source to the target, or -1 if unreachable.
     */
    public int findShortestPath(int n, List<int[]> edges, List<Integer> sources, int target) {
        // If any source is also the target, return 0 (already at the target)
        if (sources.contains(target)) {
            return 0;
        }

        // Build adjacency list with edges that have non-zero capacity
        List<Edge>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int weight = edge[2];
            int capacity = edge[3];

            // Only add edges with positive capacity
            if (capacity > 0) {
                graph[u].add(new Edge(v, weight, capacity));
            }
        }

        // Use Dijkstra's algorithm starting from all source nodes simultaneously
        int[] distances = new int[n];
        Arrays.fill(distances, Integer.MAX_VALUE);
        
        // Priority queue to get the node with the minimum distance
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(node -> node.distance));
        
        // Add all sources to the priority queue with distance 0
        for (int source : sources) {
            distances[source] = 0;
            pq.offer(new Node(source, 0));
        }
        
        // Process nodes in order of increasing distance
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.id;
            int dist = current.distance;
            
            // Skip if we have already found a better path to this node
            if (dist > distances[u]) {
                continue;
            }
            
            // If we reached the target, return the distance
            if (u == target) {
                return dist;
            }
            
            // Explore neighbors
            for (Edge edge : graph[u]) {
                int v = edge.to;
                int weight = edge.weight;
                
                // If we found a shorter path, update the distance and add to priority queue
                if (distances[u] + weight < distances[v]) {
                    distances[v] = distances[u] + weight;
                    pq.offer(new Node(v, distances[v]));
                }
            }
        }
        
        // If we can't reach the target, return -1
        return distances[target] == Integer.MAX_VALUE ? -1 : distances[target];
    }
    
    // Helper classes
    private static class Edge {
        int to;
        int weight;
        int capacity;
        
        Edge(int to, int weight, int capacity) {
            this.to = to;
            this.weight = weight;
            this.capacity = capacity;
        }
    }
    
    private static class Node {
        int id;
        int distance;
        
        Node(int id, int distance) {
            this.id = id;
            this.distance = distance;
        }
    }
}