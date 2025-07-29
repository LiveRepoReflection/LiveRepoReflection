import java.util.*;

public class NetworkReconstruction {
    
    /**
     * Reconstructs the network topology based on traffic logs.
     *
     * @param n   The number of servers in the data center
     * @param log A list of log entries with connections between servers
     * @return    An adjacency list representation of the network topology
     */
    public Map<Integer, Set<Integer>> reconstructNetwork(int n, List<LogEntry> log) {
        // Validate input
        if (n < 2) {
            throw new IllegalArgumentException("Number of servers must be at least 2");
        }
        
        // Initialize the adjacency list
        Map<Integer, Set<Integer>> network = new HashMap<>();
        for (int i = 1; i <= n; i++) {
            network.put(i, new TreeSet<>());  // Using TreeSet for sorted order
        }
        
        // Add known connections from the log
        for (LogEntry entry : log) {
            int server1 = entry.getServerId1();
            int server2 = entry.getServerId2();
            
            if (server1 < 1 || server1 > n || server2 < 1 || server2 > n) {
                throw new IllegalArgumentException("Invalid server ID in log");
            }
            
            network.get(server1).add(server2);
            network.get(server2).add(server1);
        }
        
        // If the network is disconnected, we need to infer additional connections
        if (!isConnected(network, n)) {
            connectDisconnectedComponents(network, n);
        }
        
        // Optimize the network by adding edges to minimize average path length
        optimizeNetworkTopology(network, n);
        
        return network;
    }
    
    /**
     * Checks if the network is connected (all servers can reach each other).
     */
    private boolean isConnected(Map<Integer, Set<Integer>> network, int n) {
        Set<Integer> visited = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        
        // Start BFS from node 1
        queue.add(1);
        visited.add(1);
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            
            for (int neighbor : network.get(current)) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor);
                    queue.add(neighbor);
                }
            }
        }
        
        return visited.size() == n;
    }
    
    /**
     * Connects disconnected components in the graph to ensure all servers can reach each other.
     */
    private void connectDisconnectedComponents(Map<Integer, Set<Integer>> network, int n) {
        // Find all connected components
        List<Set<Integer>> components = findConnectedComponents(network, n);
        
        // Connect each component to the next one
        for (int i = 0; i < components.size() - 1; i++) {
            int server1 = components.get(i).iterator().next();
            int server2 = components.get(i + 1).iterator().next();
            
            network.get(server1).add(server2);
            network.get(server2).add(server1);
        }
    }
    
    /**
     * Finds all connected components in the network.
     */
    private List<Set<Integer>> findConnectedComponents(Map<Integer, Set<Integer>> network, int n) {
        List<Set<Integer>> components = new ArrayList<>();
        Set<Integer> visited = new HashSet<>();
        
        for (int i = 1; i <= n; i++) {
            if (!visited.contains(i)) {
                Set<Integer> component = new HashSet<>();
                Queue<Integer> queue = new LinkedList<>();
                
                queue.add(i);
                visited.add(i);
                component.add(i);
                
                while (!queue.isEmpty()) {
                    int current = queue.poll();
                    
                    for (int neighbor : network.get(current)) {
                        if (!visited.contains(neighbor)) {
                            visited.add(neighbor);
                            queue.add(neighbor);
                            component.add(neighbor);
                        }
                    }
                }
                
                components.add(component);
            }
        }
        
        return components;
    }
    
    /**
     * Optimizes the network topology by adding edges to minimize average path length.
     * Uses Floyd-Warshall algorithm to compute all-pairs shortest paths and then
     * adds edges strategically to reduce the diameter of the network.
     */
    private void optimizeNetworkTopology(Map<Integer, Set<Integer>> network, int n) {
        // Calculate the current all-pairs shortest paths
        int[][] distances = computeAllPairsShortestPaths(network, n);
        
        // Identify potential edges to add that would most reduce the average path length
        PriorityQueue<EdgeScore> potentialEdges = new PriorityQueue<>();
        
        for (int i = 1; i <= n; i++) {
            for (int j = i + 1; j <= n; j++) {
                // Skip if there's already an edge
                if (network.get(i).contains(j)) continue;
                
                // Calculate how much this edge would reduce the average path length
                int improvement = calculateImprovementScore(distances, i, j, n);
                potentialEdges.add(new EdgeScore(i, j, improvement));
            }
        }
        
        // Add edges in order of their improvement scores
        int maxEdgesToAdd = (n * (n - 1)) / 4; // Limit the number of additional edges
        int edgesAdded = 0;
        
        while (!potentialEdges.isEmpty() && edgesAdded < maxEdgesToAdd) {
            EdgeScore edge = potentialEdges.poll();
            
            // Add this edge if it still doesn't exist
            if (!network.get(edge.node1).contains(edge.node2)) {
                network.get(edge.node1).add(edge.node2);
                network.get(edge.node2).add(edge.node1);
                
                // Update distances after adding this edge
                updateDistancesAfterAddingEdge(distances, edge.node1, edge.node2, n);
                edgesAdded++;
            }
        }
    }
    
    /**
     * Computes all-pairs shortest paths using Floyd-Warshall algorithm.
     */
    private int[][] computeAllPairsShortestPaths(Map<Integer, Set<Integer>> network, int n) {
        int[][] distances = new int[n + 1][n + 1];
        
        // Initialize distances
        for (int i = 1; i <= n; i++) {
            Arrays.fill(distances[i], Integer.MAX_VALUE / 2); // Avoid overflow
            distances[i][i] = 0;
            
            for (int j : network.get(i)) {
                distances[i][j] = 1;
            }
        }
        
        // Floyd-Warshall algorithm
        for (int k = 1; k <= n; k++) {
            for (int i = 1; i <= n; i++) {
                for (int j = 1; j <= n; j++) {
                    if (distances[i][k] + distances[k][j] < distances[i][j]) {
                        distances[i][j] = distances[i][k] + distances[k][j];
                    }
                }
            }
        }
        
        return distances;
    }
    
    /**
     * Calculates how much adding an edge between node1 and node2 would improve the network.
     */
    private int calculateImprovementScore(int[][] distances, int node1, int node2, int n) {
        int improvement = 0;
        
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                if (i == j) continue;
                
                int currentDist = distances[i][j];
                int newDist = Math.min(currentDist, 
                                       Math.min(distances[i][node1] + 1 + distances[node2][j],
                                                distances[i][node2] + 1 + distances[node1][j]));
                
                improvement += (currentDist - newDist);
            }
        }
        
        return improvement;
    }
    
    /**
     * Updates all-pairs shortest paths after adding a new edge.
     */
    private void updateDistancesAfterAddingEdge(int[][] distances, int node1, int node2, int n) {
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= n; j++) {
                distances[i][j] = Math.min(distances[i][j], 
                                        Math.min(distances[i][node1] + 1 + distances[node2][j],
                                                distances[i][node2] + 1 + distances[node1][j]));
            }
        }
    }
    
    /**
     * Helper class to score potential edges by how much they would improve the network.
     */
    private static class EdgeScore implements Comparable<EdgeScore> {
        int node1;
        int node2;
        int score;
        
        public EdgeScore(int node1, int node2, int score) {
            this.node1 = node1;
            this.node2 = node2;
            this.score = score;
        }
        
        @Override
        public int compareTo(EdgeScore other) {
            // Higher score first (max heap)
            return other.score - this.score;
        }
    }
}