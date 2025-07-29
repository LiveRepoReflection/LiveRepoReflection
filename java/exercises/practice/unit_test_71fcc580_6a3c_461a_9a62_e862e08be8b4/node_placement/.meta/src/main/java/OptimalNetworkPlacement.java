import java.util.*;

public class OptimalNetworkPlacement {

    /**
     * Finds the optimal placement of K network nodes to minimize average latency.
     *
     * @param graph             The network graph represented as an adjacency list
     * @param numExistingNodes  Number of existing nodes
     * @param k                 Number of nodes to place
     * @return                  List of node IDs where the K network nodes should be placed
     */
    public List<Integer> findOptimalPlacement(Map<Integer, List<Edge>> graph, int numExistingNodes, int k) {
        // Handle edge cases
        if (graph.isEmpty() || k == 0) {
            return new ArrayList<>();
        }
        
        if (k >= numExistingNodes) {
            // If k equals or exceeds node count, return all nodes
            List<Integer> allNodes = new ArrayList<>(graph.keySet());
            return allNodes.subList(0, Math.min(k, allNodes.size()));
        }

        // Calculate all-pairs shortest paths using Floyd-Warshall algorithm
        double[][] distances = calculateAllPairsShortestPaths(graph, numExistingNodes);
        
        // For large graphs with small k, we can use a greedy approach
        if (numExistingNodes > 100 && k <= 10) {
            return greedyPlacement(distances, numExistingNodes, k);
        }
        
        // For smaller graphs, we can try to find a more optimal solution
        return findOptimalPlacementDP(distances, numExistingNodes, k);
    }
    
    /**
     * Calculates all-pairs shortest paths using the Floyd-Warshall algorithm.
     */
    private double[][] calculateAllPairsShortestPaths(Map<Integer, List<Edge>> graph, int numNodes) {
        double[][] distances = new double[numNodes][numNodes];
        
        // Initialize distance matrix
        for (int i = 0; i < numNodes; i++) {
            Arrays.fill(distances[i], Double.POSITIVE_INFINITY);
            distances[i][i] = 0; // Distance to self is 0
        }
        
        // Initialize with direct edges
        for (int node : graph.keySet()) {
            if (node < numNodes) {
                for (Edge edge : graph.get(node)) {
                    if (edge.destination < numNodes) {
                        distances[node][edge.destination] = edge.latency;
                    }
                }
            }
        }
        
        // Floyd-Warshall algorithm
        for (int k = 0; k < numNodes; k++) {
            for (int i = 0; i < numNodes; i++) {
                for (int j = 0; j < numNodes; j++) {
                    if (distances[i][k] != Double.POSITIVE_INFINITY && 
                        distances[k][j] != Double.POSITIVE_INFINITY) {
                        distances[i][j] = Math.min(distances[i][j], distances[i][k] + distances[k][j]);
                    }
                }
            }
        }
        
        return distances;
    }
    
    /**
     * Greedy approach for placing nodes:
     * 1. Start with an empty set of selected nodes
     * 2. For each step, select the node that minimizes the average distance to the closest node
     */
    private List<Integer> greedyPlacement(double[][] distances, int numNodes, int k) {
        List<Integer> selectedNodes = new ArrayList<>();
        boolean[] isSelected = new boolean[numNodes];
        
        for (int step = 0; step < k; step++) {
            int bestNode = -1;
            double bestAvgDistance = Double.POSITIVE_INFINITY;
            
            for (int candidate = 0; candidate < numNodes; candidate++) {
                if (isSelected[candidate]) continue;
                
                // Calculate average distance if we were to add this candidate
                double totalDistance = 0;
                for (int node = 0; node < numNodes; node++) {
                    double minDistance = Double.POSITIVE_INFINITY;
                    
                    // Check distance to already selected nodes
                    for (int selected : selectedNodes) {
                        minDistance = Math.min(minDistance, distances[node][selected]);
                    }
                    
                    // Check distance to the candidate node
                    minDistance = Math.min(minDistance, distances[node][candidate]);
                    
                    totalDistance += minDistance;
                }
                
                double avgDistance = totalDistance / numNodes;
                if (avgDistance < bestAvgDistance) {
                    bestAvgDistance = avgDistance;
                    bestNode = candidate;
                }
            }
            
            // Add the best node to our selected set
            selectedNodes.add(bestNode);
            isSelected[bestNode] = true;
        }
        
        return selectedNodes;
    }
    
    /**
     * Dynamic programming approach for finding the optimal placement.
     * For small to medium sized graphs and small k, we can use bitmask DP to find the optimal solution.
     * This approach is more accurate but has exponential complexity with respect to numNodes.
     */
    private List<Integer> findOptimalPlacementDP(double[][] distances, int numNodes, int k) {
        // For larger graphs, we'll limit the DP approach to a smaller subset of nodes
        // We can focus on promising candidates using centrality metrics
        List<Integer> candidates;
        if (numNodes > 20) {
            // Use centrality metrics to prune search space
            candidates = selectTopCandidatesByCloseness(distances, numNodes, Math.min(20, numNodes));
        } else {
            candidates = new ArrayList<>();
            for (int i = 0; i < numNodes; i++) {
                candidates.add(i);
            }
        }
        
        int n = candidates.size();
        int maxState = 1 << n;  // 2^n states for the DP approach
        
        // dp[state] = min average distance when the nodes in 'state' are selected
        double[] dp = new double[maxState];
        int[] prevState = new int[maxState];
        
        Arrays.fill(dp, Double.POSITIVE_INFINITY);
        dp[0] = 0;  // Base case: no nodes selected
        
        // Iterate through all possible states
        for (int state = 0; state < maxState; state++) {
            if (Integer.bitCount(state) > k) continue;  // Skip if more than k nodes are selected
            
            // Try adding one more node
            for (int nextNode = 0; nextNode < n; nextNode++) {
                if ((state & (1 << nextNode)) != 0) continue;  // Skip if node already selected
                
                int newState = state | (1 << nextNode);
                
                // Calculate the average distance with the new state
                double avgDistance = calculateAverageDistance(distances, candidates, newState, numNodes);
                
                if (avgDistance < dp[newState]) {
                    dp[newState] = avgDistance;
                    prevState[newState] = state;
                }
            }
        }
        
        // Find the best state with exactly k nodes
        int bestState = -1;
        double bestAvgDistance = Double.POSITIVE_INFINITY;
        
        for (int state = 0; state < maxState; state++) {
            if (Integer.bitCount(state) == k && dp[state] < bestAvgDistance) {
                bestAvgDistance = dp[state];
                bestState = state;
            }
        }
        
        // Reconstruct the selected nodes
        List<Integer> selectedNodes = new ArrayList<>();
        if (bestState != -1) {
            for (int i = 0; i < n; i++) {
                if ((bestState & (1 << i)) != 0) {
                    selectedNodes.add(candidates.get(i));
                }
            }
        }
        
        return selectedNodes;
    }
    
    /**
     * Calculates the average distance from each node to its closest selected node.
     */
    private double calculateAverageDistance(double[][] distances, List<Integer> candidates, int state, int numNodes) {
        double totalDistance = 0;
        
        for (int node = 0; node < numNodes; node++) {
            double minDistance = Double.POSITIVE_INFINITY;
            
            for (int i = 0; i < candidates.size(); i++) {
                if ((state & (1 << i)) != 0) {  // If the i-th candidate is selected
                    int selectedNode = candidates.get(i);
                    minDistance = Math.min(minDistance, distances[node][selectedNode]);
                }
            }
            
            totalDistance += minDistance;
        }
        
        return totalDistance / numNodes;
    }
    
    /**
     * Selects the top N candidates based on closeness centrality.
     * Closeness centrality of a node is defined as the reciprocal of the sum of 
     * the shortest path distances from the node to all other nodes.
     */
    private List<Integer> selectTopCandidatesByCloseness(double[][] distances, int numNodes, int topN) {
        // Calculate closeness centrality for all nodes
        double[] centrality = new double[numNodes];
        
        for (int node = 0; node < numNodes; node++) {
            double sum = 0;
            for (int other = 0; other < numNodes; other++) {
                if (distances[node][other] != Double.POSITIVE_INFINITY) {
                    sum += distances[node][other];
                } else {
                    // Handle disconnected nodes
                    sum += numNodes * 1000;  // Large penalty for disconnected components
                }
            }
            centrality[node] = (sum > 0) ? 1.0 / sum : 0;
        }
        
        // Create node indices and sort by centrality
        Integer[] nodeIndices = new Integer[numNodes];
        for (int i = 0; i < numNodes; i++) {
            nodeIndices[i] = i;
        }
        
        Arrays.sort(nodeIndices, (a, b) -> Double.compare(centrality[b], centrality[a]));
        
        // Select top candidates
        List<Integer> candidates = new ArrayList<>();
        for (int i = 0; i < Math.min(topN, numNodes); i++) {
            candidates.add(nodeIndices[i]);
        }
        
        return candidates;
    }
}