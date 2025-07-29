import java.util.*;

public class NetworkPaths implements NetworkPathsInterface {
    private final int numNodes;
    private final double congestionFactor;
    private final Map<Integer, Map<Integer, Integer>> graph; // adjacency list: source -> (target -> latency)
    private final Map<String, Integer> congestionLevels; // edge identifier -> congestion count

    /**
     * Initializes the NetworkPaths with the given edges, number of nodes, and congestion factor
     * 
     * @param edges Array of [source, destination, latency] edges
     * @param n Number of nodes in the network
     * @param c Congestion factor
     */
    public NetworkPaths(int[][] edges, int n, double c) {
        numNodes = n;
        congestionFactor = c;
        graph = new HashMap<>();
        congestionLevels = new HashMap<>();

        // Initialize graph
        for (int i = 0; i < n; i++) {
            graph.put(i, new HashMap<>());
        }

        // Add initial edges
        for (int[] edge : edges) {
            int source = edge[0];
            int destination = edge[1];
            int latency = edge[2];
            graph.get(source).put(destination, latency);
            congestionLevels.put(edgeKey(source, destination), 0);
        }
    }

    /**
     * Updates the latency of an edge in the network
     * 
     * @param source The source node
     * @param destination The destination node
     * @param newLatency The new latency value
     */
    @Override
    public void updateLatency(int source, int destination, int newLatency) {
        if (!graph.containsKey(source)) {
            graph.put(source, new HashMap<>());
        }
        graph.get(source).put(destination, newLatency);
        
        // Ensure congestion level exists for this edge
        congestionLevels.putIfAbsent(edgeKey(source, destination), 0);
    }

    /**
     * Finds the k shortest paths from source to destination
     * 
     * @param source The source node
     * @param destination The destination node
     * @param k The number of paths to find
     * @return A list of paths, where each path is a list of node IDs
     */
    @Override
    public List<List<Integer>> findShortestPaths(int source, int destination, int k) {
        // Check if source and destination are valid
        if (source < 0 || source >= numNodes || destination < 0 || destination >= numNodes) {
            return new ArrayList<>();
        }
        
        // Temporary set to store edges used in current path finding to avoid double counting congestion
        Set<String> currentPathEdges = new HashSet<>();
        
        // Initialize result list to store k shortest paths
        List<List<Integer>> kShortestPaths = new ArrayList<>();
        
        // Use a modified version of Yen's algorithm for k-shortest paths
        // First, find the shortest path using Dijkstra's algorithm
        List<Integer> shortestPath = findShortestPath(source, destination);
        if (shortestPath.isEmpty()) {
            return kShortestPaths; // No path exists
        }
        
        // Add the first shortest path to the result
        kShortestPaths.add(shortestPath);
        
        // Update congestion levels for the first path
        updateCongestion(shortestPath);
        
        // Priority queue to store candidate paths
        PriorityQueue<PathWithCost> candidates = new PriorityQueue<>();
        
        // Set to keep track of paths we've already considered to avoid duplicates
        Set<List<Integer>> consideredPaths = new HashSet<>();
        consideredPaths.add(shortestPath);
        
        // Find k-1 more paths
        for (int i = 1; i < k; i++) {
            if (kShortestPaths.size() < i) {
                break; // No more paths possible
            }
            
            List<Integer> prevPath = kShortestPaths.get(i - 1);
            
            // For each node in the previous path (except destination)
            for (int j = 0; j < prevPath.size() - 1; j++) {
                int spurNode = prevPath.get(j);
                List<Integer> rootPath = new ArrayList<>(prevPath.subList(0, j + 1));
                
                // Store the original graph
                Map<Integer, Map<Integer, Integer>> originalGraph = new HashMap<>();
                for (int node : graph.keySet()) {
                    originalGraph.put(node, new HashMap<>(graph.get(node)));
                }
                
                // Store original congestion levels
                Map<String, Integer> originalCongestion = new HashMap<>(congestionLevels);
                
                // Remove edges that are part of previous k shortest paths with the same root
                for (List<Integer> path : kShortestPaths) {
                    if (path.size() > j + 1 && path.subList(0, j + 1).equals(rootPath)) {
                        int rootNode = path.get(j);
                        int nextNode = path.get(j + 1);
                        // Temporarily remove the edge to force finding an alternative path
                        if (graph.containsKey(rootNode)) {
                            graph.get(rootNode).remove(nextNode);
                        }
                    }
                }
                
                // Remove all edges going out from nodes in rootPath except spurNode
                for (int n = 0; n < j; n++) {
                    int node = rootPath.get(n);
                    if (graph.containsKey(node)) {
                        graph.put(node, new HashMap<>());
                    }
                }
                
                // Find the shortest path from spurNode to destination
                List<Integer> spurPath = findShortestPath(spurNode, destination);
                
                // Restore the original graph and congestion levels
                graph.clear();
                graph.putAll(originalGraph);
                congestionLevels.clear();
                congestionLevels.putAll(originalCongestion);
                
                if (!spurPath.isEmpty()) {
                    // Build the complete path by concatenating rootPath and spurPath (without first element)
                    List<Integer> totalPath = new ArrayList<>(rootPath);
                    totalPath.addAll(spurPath.subList(1, spurPath.size()));
                    
                    // Add to candidates if it's a new path
                    if (!consideredPaths.contains(totalPath)) {
                        double pathCost = calculatePathCost(totalPath);
                        candidates.add(new PathWithCost(totalPath, pathCost));
                        consideredPaths.add(totalPath);
                    }
                }
            }
            
            // Get the next best path
            if (!candidates.isEmpty()) {
                PathWithCost nextBest = candidates.poll();
                kShortestPaths.add(nextBest.path);
                updateCongestion(nextBest.path);
            } else {
                // No more paths exist
                break;
            }
        }
        
        return kShortestPaths;
    }

    /**
     * Finds the shortest path from source to destination considering congestion
     * 
     * @param source Source node
     * @param destination Destination node
     * @return List of nodes representing the path, empty if no path exists
     */
    private List<Integer> findShortestPath(int source, int destination) {
        // Use Dijkstra's algorithm with congestion-aware edge weights
        PriorityQueue<NodeWithDistance> pq = new PriorityQueue<>();
        Map<Integer, Double> distances = new HashMap<>();
        Map<Integer, Integer> previousNode = new HashMap<>();
        Set<Integer> visited = new HashSet<>();
        
        // Initialize distances
        for (int i = 0; i < numNodes; i++) {
            distances.put(i, Double.POSITIVE_INFINITY);
        }
        distances.put(source, 0.0);
        pq.add(new NodeWithDistance(source, 0.0));
        
        while (!pq.isEmpty() && !visited.contains(destination)) {
            NodeWithDistance current = pq.poll();
            int currentNode = current.node;
            double currentDistance = current.distance;
            
            if (visited.contains(currentNode)) {
                continue;
            }
            
            visited.add(currentNode);
            
            // Process all neighbors
            if (graph.containsKey(currentNode)) {
                for (Map.Entry<Integer, Integer> neighbor : graph.get(currentNode).entrySet()) {
                    int nextNode = neighbor.getKey();
                    if (visited.contains(nextNode)) {
                        continue;
                    }
                    
                    // Calculate edge weight with congestion penalty
                    double edgeWeight = calculateEffectiveLatency(currentNode, nextNode);
                    
                    double newDistance = currentDistance + edgeWeight;
                    if (newDistance < distances.get(nextNode)) {
                        distances.put(nextNode, newDistance);
                        previousNode.put(nextNode, currentNode);
                        pq.add(new NodeWithDistance(nextNode, newDistance));
                    }
                }
            }
        }
        
        // Reconstruct path
        if (!previousNode.containsKey(destination) && source != destination) {
            return new ArrayList<>(); // No path exists
        }
        
        List<Integer> path = new ArrayList<>();
        int node = destination;
        while (node != source) {
            path.add(node);
            node = previousNode.get(node);
        }
        path.add(source);
        Collections.reverse(path);
        
        return path;
    }
    
    /**
     * Calculates the total cost (effective latency) of a path
     * 
     * @param path List of nodes representing the path
     * @return Total effective latency of the path
     */
    private double calculatePathCost(List<Integer> path) {
        double totalCost = 0;
        for (int i = 0; i < path.size() - 1; i++) {
            int source = path.get(i);
            int destination = path.get(i + 1);
            totalCost += calculateEffectiveLatency(source, destination);
        }
        return totalCost;
    }
    
    /**
     * Calculates the effective latency of an edge considering congestion
     * 
     * @param source Source node
     * @param destination Destination node
     * @return Effective latency
     */
    private double calculateEffectiveLatency(int source, int destination) {
        String edge = edgeKey(source, destination);
        int baseLatency = graph.get(source).get(destination);
        int congestion = congestionLevels.getOrDefault(edge, 0);
        return baseLatency * (1 + congestion * congestionFactor);
    }
    
    /**
     * Updates congestion levels for all edges in a path
     * 
     * @param path List of nodes representing the path
     */
    private void updateCongestion(List<Integer> path) {
        for (int i = 0; i < path.size() - 1; i++) {
            String edge = edgeKey(path.get(i), path.get(i + 1));
            congestionLevels.put(edge, congestionLevels.getOrDefault(edge, 0) + 1);
        }
    }
    
    /**
     * Creates a unique key for an edge
     * 
     * @param source Source node
     * @param destination Destination node
     * @return String key
     */
    private String edgeKey(int source, int destination) {
        return source + "->" + destination;
    }
    
    /**
     * Helper class to store a node with its distance for Dijkstra's algorithm
     */
    private static class NodeWithDistance implements Comparable<NodeWithDistance> {
        int node;
        double distance;
        
        NodeWithDistance(int node, double distance) {
            this.node = node;
            this.distance = distance;
        }
        
        @Override
        public int compareTo(NodeWithDistance other) {
            return Double.compare(this.distance, other.distance);
        }
    }
    
    /**
     * Helper class to store a path with its cost for the priority queue
     */
    private static class PathWithCost implements Comparable<PathWithCost> {
        List<Integer> path;
        double cost;
        
        PathWithCost(List<Integer> path, double cost) {
            this.path = path;
            this.cost = cost;
        }
        
        @Override
        public int compareTo(PathWithCost other) {
            return Double.compare(this.cost, other.cost);
        }
    }
}