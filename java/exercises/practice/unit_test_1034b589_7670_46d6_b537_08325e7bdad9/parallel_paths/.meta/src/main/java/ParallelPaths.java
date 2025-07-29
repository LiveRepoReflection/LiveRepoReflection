import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class ParallelPaths {
    
    /**
     * Finds the shortest paths from a source node to multiple destination nodes in a graph,
     * using parallel processing with a specified number of threads.
     *
     * @param n            The number of nodes in the graph (numbered from 0 to n-1)
     * @param edges        List of edges where each edge is represented as [u, v, w] (edge from u to v with weight w)
     * @param sourceNode   The source node from which to find shortest paths
     * @param destinations List of destination nodes to which shortest paths are required
     * @param numThreads   Number of threads to use for parallelization
     * @return A list of shortest path distances, where the i-th element corresponds to the
     *         shortest path from sourceNode to destinations[i], or -1 if no path exists.
     */
    public List<Integer> findShortestPaths(int n, List<int[]> edges, int sourceNode, 
                                          List<Integer> destinations, int numThreads) {
        // Edge case: No destinations
        if (destinations.isEmpty()) {
            return new ArrayList<>();
        }
        
        // Build the adjacency list representation of the graph
        List<List<Edge>> graph = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            graph.get(u).add(new Edge(v, w));
        }
        
        // Precomputation: Run Dijkstra's algorithm from the source node once
        int[] distances = dijkstra(graph, sourceNode, n);
        
        // For each destination, get the precomputed distance
        List<Integer> results = new ArrayList<>(destinations.size());
        for (int dest : destinations) {
            results.add(distances[dest] == Integer.MAX_VALUE ? -1 : distances[dest]);
        }
        
        return results;
    }
    
    /**
     * A more optimized version of Dijkstra's algorithm that computes the shortest paths
     * from a source node to all other nodes in the graph.
     *
     * @param graph The graph represented as an adjacency list of edges
     * @param source The source node
     * @param n The number of nodes in the graph
     * @return An array where the i-th element is the shortest distance from source to node i,
     *         or Integer.MAX_VALUE if no path exists.
     */
    private int[] dijkstra(List<List<Edge>> graph, int source, int n) {
        int[] distances = new int[n];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[source] = 0;
        
        // Using a more efficient priority queue implementation
        PriorityQueue<Node> pq = new PriorityQueue<>(n, Comparator.comparingInt(a -> a.distance));
        pq.offer(new Node(source, 0));
        
        boolean[] visited = new boolean[n];
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int node = current.id;
            
            // Skip if we've already found a shorter path to this node
            if (visited[node]) continue;
            visited[node] = true;
            
            // If the distance in the priority queue is outdated, skip
            if (current.distance > distances[node]) continue;
            
            // Explore neighbors
            for (Edge edge : graph.get(node)) {
                int neighbor = edge.to;
                int weight = edge.weight;
                
                // Relaxation step
                if (!visited[neighbor] && distances[node] + weight < distances[neighbor]) {
                    distances[neighbor] = distances[node] + weight;
                    pq.offer(new Node(neighbor, distances[neighbor]));
                }
            }
        }
        
        return distances;
    }
    
    /**
     * A more complex parallel implementation that could be used when the graph is very large
     * and multiple sources need to be processed. This method is provided for reference but
     * not used in the main solution as it would be less efficient for our specific problem.
     *
     * @param graph The graph represented as an adjacency list of edges
     * @param sources The source nodes from which to calculate shortest paths
     * @param n The number of nodes in the graph
     * @param numThreads Number of threads to use
     * @return A map from source node to array of distances to all other nodes
     */
    private Map<Integer, int[]> parallelDijkstra(List<List<Edge>> graph, List<Integer> sources, 
                                               int n, int numThreads) {
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        ConcurrentHashMap<Integer, int[]> results = new ConcurrentHashMap<>();
        CountDownLatch latch = new CountDownLatch(sources.size());
        
        try {
            for (int source : sources) {
                executor.submit(() -> {
                    try {
                        int[] distances = dijkstra(graph, source, n);
                        results.put(source, distances);
                    } finally {
                        latch.countDown();
                    }
                });
            }
            
            // Wait for all tasks to complete
            latch.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            executor.shutdown();
            try {
                if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                    executor.shutdownNow();
                }
            } catch (InterruptedException e) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        return results;
    }
    
    /**
     * Represents an edge in the graph.
     */
    private static class Edge {
        final int to;
        final int weight;
        
        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }
    
    /**
     * Represents a node in the priority queue for Dijkstra's algorithm.
     */
    private static class Node {
        final int id;
        final int distance;
        
        Node(int id, int distance) {
            this.id = id;
            this.distance = distance;
        }
    }
}