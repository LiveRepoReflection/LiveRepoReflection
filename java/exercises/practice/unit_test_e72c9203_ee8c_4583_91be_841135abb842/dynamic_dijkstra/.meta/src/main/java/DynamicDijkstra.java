import java.util.*;

public class DynamicDijkstra {
    private int n; // number of nodes
    private Map<Integer, Map<Integer, Long>> graph; // adjacency list representation
    private Set<Integer> sources; // set of source nodes
    private boolean isDirty; // flag to indicate if graph has been modified since last computation
    private int[] lastComputedDistances; // cache for the last computed distances

    public void initialize(int n, int[][] edges) {
        this.n = n;
        this.graph = new HashMap<>();
        this.sources = new HashSet<>();
        this.isDirty = true;
        this.lastComputedDistances = null;

        // Initialize empty adjacency lists for all nodes
        for (int i = 0; i < n; i++) {
            graph.put(i, new HashMap<>());
        }

        // Add all edges to the graph
        for (int[] edge : edges) {
            updateEdge(edge[0], edge[1], edge[2]);
        }
    }

    public void setSources(List<Integer> sourceNodes) {
        this.sources.clear();
        this.sources.addAll(sourceNodes);
        this.isDirty = true;
    }

    public void updateEdge(int u, int v, int w) {
        if (!graph.containsKey(u)) {
            graph.put(u, new HashMap<>());
        }
        graph.get(u).put(v, (long) w);
        this.isDirty = true;
    }

    public int[] getShortestPaths() {
        if (!isDirty && lastComputedDistances != null) {
            return lastComputedDistances.clone();
        }

        // Initialize distances array
        int[] distances = new int[n];
        Arrays.fill(distances, Integer.MAX_VALUE);

        // Priority queue to store nodes and their distances
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingLong(node -> node.distance));

        // Initialize distances for source nodes
        for (int source : sources) {
            distances[source] = 0;
            pq.offer(new Node(source, 0));
        }

        // Set to keep track of processed nodes
        Set<Integer> processed = new HashSet<>();

        // Process nodes
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            int u = current.vertex;

            // Skip if we've already processed this node with a shorter distance
            if (processed.contains(u) || current.distance > distances[u]) {
                continue;
            }

            processed.add(u);

            // Process all neighbors of the current node
            if (graph.containsKey(u)) {
                for (Map.Entry<Integer, Long> edge : graph.get(u).entrySet()) {
                    int v = edge.getKey();
                    long weight = edge.getValue();

                    // Check if we can improve the distance to neighbor
                    if (!processed.contains(v) && 
                        distances[u] != Integer.MAX_VALUE && 
                        distances[u] + weight < Integer.MAX_VALUE) {
                        
                        long newDist = distances[u] + weight;
                        if (newDist < distances[v]) {
                            distances[v] = (int) newDist;
                            pq.offer(new Node(v, newDist));
                        }
                    }
                }
            }
        }

        // Cache the results
        this.lastComputedDistances = distances;
        this.isDirty = false;

        return distances;
    }

    private static class Node {
        int vertex;
        long distance;

        Node(int vertex, long distance) {
            this.vertex = vertex;
            this.distance = distance;
        }
    }
}