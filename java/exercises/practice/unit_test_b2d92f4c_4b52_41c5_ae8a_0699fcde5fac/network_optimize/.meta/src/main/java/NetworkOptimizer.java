import java.util.*;

public class NetworkOptimizer {
    
    /**
     * Optimizes a network by performing edge swaps to minimize the maximum latency.
     * 
     * @param network A list of lists representing the adjacency list of the network.
     *                network.get(i) contains a list of server IDs directly connected to server i.
     * @param k The maximum number of edge swaps allowed.
     * @return The minimum possible maximum latency achievable after performing at most k edge swaps.
     * @throws IllegalArgumentException if the input is invalid.
     */
    public int optimizeNetwork(List<List<Integer>> network, int k) {
        // Validate inputs
        if (network == null || network.isEmpty()) {
            throw new IllegalArgumentException("Network cannot be empty");
        }
        
        if (k < 0) {
            throw new IllegalArgumentException("Number of allowed swaps cannot be negative");
        }
        
        int n = network.size();
        
        // Create adjacency matrix for easier manipulation
        boolean[][] adjacencyMatrix = createAdjacencyMatrix(network);
        
        // Check if the initial network is connected (if k is 0)
        if (k == 0) {
            if (!isConnected(adjacencyMatrix)) {
                throw new IllegalArgumentException("Initial network must be connected");
            }
            return calculateMaxLatency(adjacencyMatrix);
        }
        
        // If the initial network is not connected but k > 0, we try to connect it
        if (!isConnected(adjacencyMatrix)) {
            return optimizeDisconnectedNetwork(network, adjacencyMatrix, k);
        }
        
        // Calculate current max latency
        int currentMaxLatency = calculateMaxLatency(adjacencyMatrix);
        
        // If the network is already a complete graph, return 1
        if (currentMaxLatency == 1) {
            return 1;
        }
        
        // Try to optimize using a heuristic approach
        return optimizeConnectedNetwork(adjacencyMatrix, k);
    }
    
    /**
     * Attempts to optimize a disconnected network by first connecting it
     * and then further optimizing if possible.
     */
    private int optimizeDisconnectedNetwork(List<List<Integer>> network, boolean[][] adjacencyMatrix, int k) {
        // Identify the connected components
        int n = network.size();
        int[] components = findConnectedComponents(adjacencyMatrix);
        Set<Integer> distinctComponents = new HashSet<>();
        for (int component : components) {
            distinctComponents.add(component);
        }
        
        int numComponents = distinctComponents.size();
        
        // Need at least numComponents-1 swaps to connect all components
        if (numComponents-1 > k) {
            throw new IllegalArgumentException("Initial network must be connected");
        }
        
        // Connect the components greedily
        int swapsUsed = connectComponents(adjacencyMatrix, components, numComponents);
        
        // Use remaining swaps for further optimization
        int remainingSwaps = k - swapsUsed;
        if (remainingSwaps > 0) {
            return optimizeConnectedNetwork(adjacencyMatrix, remainingSwaps);
        } else {
            return calculateMaxLatency(adjacencyMatrix);
        }
    }
    
    /**
     * Connects disconnected components in the network, returning the number of swaps used.
     */
    private int connectComponents(boolean[][] adjacencyMatrix, int[] components, int numComponents) {
        int n = adjacencyMatrix.length;
        int swapsUsed = 0;
        
        // Find a representative node for each component
        Map<Integer, Integer> componentReps = new HashMap<>();
        for (int i = 0; i < n; i++) {
            componentReps.putIfAbsent(components[i], i);
        }
        
        // Connect components one by one
        int firstComponentId = components[0];
        for (int compId : componentReps.keySet()) {
            if (compId != firstComponentId) {
                int node1 = componentReps.get(firstComponentId);
                int node2 = componentReps.get(compId);
                
                // Add edge between the two components
                adjacencyMatrix[node1][node2] = true;
                adjacencyMatrix[node2][node1] = true;
                swapsUsed++;
            }
        }
        
        return swapsUsed;
    }
    
    /**
     * Attempts to optimize a connected network by strategically adding edges to
     * reduce the diameter of the network.
     */
    private int optimizeConnectedNetwork(boolean[][] adjacencyMatrix, int k) {
        int n = adjacencyMatrix.length;
        
        // Calculate all-pairs shortest paths using Floyd-Warshall algorithm
        int[][] distances = calculateAllPairsShortestPaths(adjacencyMatrix);
        
        // Keep track of our best result
        int bestLatency = calculateMaxLatencyFromDistances(distances);
        boolean[][] bestAdjacencyMatrix = deepCopyAdjacencyMatrix(adjacencyMatrix);
        
        // Use a greedy approach: in each step, find the edge that reduces the max latency the most
        for (int swap = 0; swap < k; swap++) {
            int bestNewLatency = bestLatency;
            int bestU = -1, bestV = -1;
            int[][] bestNewDistances = null;
            
            // Try all possible edge additions (that don't already exist)
            for (int u = 0; u < n; u++) {
                for (int v = u + 1; v < n; v++) {
                    if (!bestAdjacencyMatrix[u][v]) {  // If edge doesn't exist
                        // Simulate adding this edge
                        int[][] newDistances = simulateAddEdge(distances, u, v);
                        int newMaxLatency = calculateMaxLatencyFromDistances(newDistances);
                        
                        if (newMaxLatency < bestNewLatency) {
                            bestNewLatency = newMaxLatency;
                            bestU = u;
                            bestV = v;
                            bestNewDistances = newDistances;
                        }
                    }
                }
            }
            
            // If we found a better configuration, update our state
            if (bestU != -1) {
                bestLatency = bestNewLatency;
                bestAdjacencyMatrix[bestU][bestV] = true;
                bestAdjacencyMatrix[bestV][bestU] = true;
                distances = bestNewDistances;
                
                // If we've reached the theoretical minimum latency (1), we can stop
                if (bestLatency == 1) {
                    break;
                }
            } else {
                // If no improvement was possible, break early
                break;
            }
        }
        
        return bestLatency;
    }
    
    /**
     * Creates an adjacency matrix representation from an adjacency list.
     */
    private boolean[][] createAdjacencyMatrix(List<List<Integer>> network) {
        int n = network.size();
        boolean[][] adjacencyMatrix = new boolean[n][n];
        
        for (int i = 0; i < n; i++) {
            for (int neighbor : network.get(i)) {
                if (neighbor < 0 || neighbor >= n) {
                    throw new IllegalArgumentException("Invalid edge in network");
                }
                adjacencyMatrix[i][neighbor] = true;
            }
        }
        
        return adjacencyMatrix;
    }
    
    /**
     * Calculates the maximum latency (diameter) of the network.
     */
    private int calculateMaxLatency(boolean[][] adjacencyMatrix) {
        int[][] distances = calculateAllPairsShortestPaths(adjacencyMatrix);
        return calculateMaxLatencyFromDistances(distances);
    }
    
    /**
     * Calculates all-pairs shortest paths using the Floyd-Warshall algorithm.
     */
    private int[][] calculateAllPairsShortestPaths(boolean[][] adjacencyMatrix) {
        int n = adjacencyMatrix.length;
        int[][] distances = new int[n][n];
        
        // Initialize distances
        for (int i = 0; i < n; i++) {
            Arrays.fill(distances[i], Integer.MAX_VALUE / 2);  // Avoid overflow
            distances[i][i] = 0;
            
            for (int j = 0; j < n; j++) {
                if (adjacencyMatrix[i][j]) {
                    distances[i][j] = 1;
                }
            }
        }
        
        // Floyd-Warshall algorithm
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (distances[i][k] + distances[k][j] < distances[i][j]) {
                        distances[i][j] = distances[i][k] + distances[k][j];
                    }
                }
            }
        }
        
        return distances;
    }
    
    /**
     * Calculates the maximum latency from the all-pairs shortest paths.
     */
    private int calculateMaxLatencyFromDistances(int[][] distances) {
        int n = distances.length;
        int maxLatency = 0;
        
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    // If nodes are not connected, the graph is disconnected
                    if (distances[i][j] == Integer.MAX_VALUE / 2) {
                        return Integer.MAX_VALUE / 2;
                    }
                    maxLatency = Math.max(maxLatency, distances[i][j]);
                }
            }
        }
        
        return maxLatency;
    }
    
    /**
     * Simulates adding an edge between nodes u and v and recalculates distances.
     */
    private int[][] simulateAddEdge(int[][] currentDistances, int u, int v) {
        int n = currentDistances.length;
        int[][] newDistances = deepCopyDistances(currentDistances);
        
        // Update distances considering the new edge (u, v) with weight 1
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                // Try path through the new edge
                int throughU = newDistances[i][u] + 1 + newDistances[v][j];
                int throughV = newDistances[i][v] + 1 + newDistances[u][j];
                
                // Update if a shorter path is found
                newDistances[i][j] = Math.min(newDistances[i][j], Math.min(throughU, throughV));
            }
        }
        
        return newDistances;
    }
    
    /**
     * Creates a deep copy of the distances matrix.
     */
    private int[][] deepCopyDistances(int[][] distances) {
        int n = distances.length;
        int[][] copy = new int[n][n];
        
        for (int i = 0; i < n; i++) {
            System.arraycopy(distances[i], 0, copy[i], 0, n);
        }
        
        return copy;
    }
    
    /**
     * Creates a deep copy of the adjacency matrix.
     */
    private boolean[][] deepCopyAdjacencyMatrix(boolean[][] matrix) {
        int n = matrix.length;
        boolean[][] copy = new boolean[n][n];
        
        for (int i = 0; i < n; i++) {
            System.arraycopy(matrix[i], 0, copy[i], 0, n);
        }
        
        return copy;
    }
    
    /**
     * Checks if the network is connected using BFS.
     */
    private boolean isConnected(boolean[][] adjacencyMatrix) {
        int n = adjacencyMatrix.length;
        if (n == 0) return true;
        
        boolean[] visited = new boolean[n];
        Queue<Integer> queue = new LinkedList<>();
        
        queue.offer(0);
        visited[0] = true;
        
        while (!queue.isEmpty()) {
            int node = queue.poll();
            
            for (int neighbor = 0; neighbor < n; neighbor++) {
                if (adjacencyMatrix[node][neighbor] && !visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.offer(neighbor);
                }
            }
        }
        
        // Check if all nodes are visited
        for (boolean v : visited) {
            if (!v) return false;
        }
        
        return true;
    }
    
    /**
     * Finds the connected components in the network using DFS.
     */
    private int[] findConnectedComponents(boolean[][] adjacencyMatrix) {
        int n = adjacencyMatrix.length;
        int[] components = new int[n];
        Arrays.fill(components, -1);
        int componentId = 0;
        
        for (int i = 0; i < n; i++) {
            if (components[i] == -1) {
                dfs(adjacencyMatrix, i, components, componentId);
                componentId++;
            }
        }
        
        return components;
    }
    
    /**
     * Helper method for DFS to identify connected components.
     */
    private void dfs(boolean[][] adjacencyMatrix, int node, int[] components, int componentId) {
        components[node] = componentId;
        
        for (int neighbor = 0; neighbor < adjacencyMatrix.length; neighbor++) {
            if (adjacencyMatrix[node][neighbor] && components[neighbor] == -1) {
                dfs(adjacencyMatrix, neighbor, components, componentId);
            }
        }
    }
}