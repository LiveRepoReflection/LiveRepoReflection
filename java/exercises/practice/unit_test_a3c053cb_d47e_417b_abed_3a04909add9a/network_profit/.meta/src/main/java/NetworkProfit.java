import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class NetworkProfit {

    // Edge class to represent a link in the candidate subgraph (undirected)
    private static class Edge {
        int u;
        int v;
        int cost;
        Edge(int u, int v, int cost) {
            this.u = u;
            this.v = v;
            this.cost = cost;
        }
    }
    
    /**
     * Computes the maximum profit achievable given the network deployment constraints.
     *
     * @param numTowns Number of towns (nodes) in the graph.
     * @param townPopulations Array with the revenue (population) for each town.
     * @param linkCosts 2D array representing edges as {town1, town2, cost}.
     * @param budget The maximum total cost allowed for deploying fiber optic links.
     * @return Maximum profit = (sum of selected town revenues) - (cable cost), subject to constraints.
     */
    public static int computeMaxProfit(int numTowns, int[] townPopulations, int[][] linkCosts, int budget) {
        // For each potential subgraph, we want to maximize (revenue - cost),
        // where the cost does not exceed the budget, and the chosen subgraph is 
        // 2-edge-connected if it has at least 2 nodes.
        
        int maxProfit = Integer.MIN_VALUE;
        
        // Pre-calculate best single node option. A single town does not require links.
        for (int i = 0; i < numTowns; i++) {
            if (townPopulations[i] > maxProfit && townPopulations[i] <= budget + townPopulations[i]) {
                // As cost is 0, profit equals the population.
                maxProfit = Math.max(maxProfit, townPopulations[i]);
            }
        }
        
        // If the number of towns is small, we enumerate all nonempty subsets.
        // Otherwise, we try a limited search by enumerating subsets of size up to 3.
        if (numTowns <= 10) {
            // Enumerate all subsets of towns (using bitmask representation).
            int totalSubsets = 1 << numTowns;
            for (int mask = 1; mask < totalSubsets; mask++) {
                List<Integer> subsetNodes = new ArrayList<>();
                int revenue = 0;
                for (int i = 0; i < numTowns; i++) {
                    if (((mask >> i) & 1) == 1) {
                        subsetNodes.add(i);
                        revenue += townPopulations[i];
                    }
                }
                int bestCost = 0;
                if (subsetNodes.size() == 1) {
                    // A single node subgraph requires no cable.
                    bestCost = 0;
                } else {
                    // Find the minimum cost to build a subgraph on these nodes that is:
                    // 1. Connected.
                    // 2. Two-edge-connected (remains connected after removal of any one edge).
                    bestCost = findMinCostFor2EdgeConnected(subsetNodes, linkCosts);
                    if (bestCost == -1) {
                        continue; // not possible to build a reliable subgraph on these nodes.
                    }
                }
                if (bestCost <= budget) {
                    maxProfit = Math.max(maxProfit, revenue - bestCost);
                }
            }
        } else {
            // For larger graphs, due to NP-hard complexity, we try with limited subset sizes.
            // We consider all subsets of size 1, 2, and 3.
            List<List<Integer>> subsets = new ArrayList<>();
            // size 1 subsets are already handled.
            // size 2
            for (int i = 0; i < numTowns; i++) {
                for (int j = i + 1; j < numTowns; j++) {
                    List<Integer> list = new ArrayList<>();
                    list.add(i);
                    list.add(j);
                    subsets.add(list);
                }
            }
            // size 3
            for (int i = 0; i < numTowns; i++) {
                for (int j = i + 1; j < numTowns; j++) {
                    for (int k = j + 1; k < numTowns; k++) {
                        List<Integer> list = new ArrayList<>();
                        list.add(i);
                        list.add(j);
                        list.add(k);
                        subsets.add(list);
                    }
                }
            }
            for (List<Integer> subsetNodes : subsets) {
                int revenue = 0;
                for (Integer node : subsetNodes) {
                    revenue += townPopulations[node];
                }
                int bestCost = findMinCostFor2EdgeConnected(subsetNodes, linkCosts);
                if (bestCost == -1)
                    continue;
                if (bestCost <= budget) {
                    maxProfit = Math.max(maxProfit, revenue - bestCost);
                }
            }
        }
        
        return maxProfit;
    }
    
    // Given a list of nodes (subsetNodes) and available links (linkCosts),
    // find the minimum total cost to obtain a subgraph that is connected and 2-edge-connected.
    // If not possible, return -1.
    private static int findMinCostFor2EdgeConnected(List<Integer> subsetNodes, int[][] linkCosts) {
        // Collect candidate edges whose both endpoints are in subsetNodes.
        Set<Integer> nodeSet = new HashSet<>(subsetNodes);
        List<Edge> candidateEdges = new ArrayList<>();
        for (int[] link : linkCosts) {
            int u = link[0];
            int v = link[1];
            int cost = link[2];
            if (nodeSet.contains(u) && nodeSet.contains(v)) {
                candidateEdges.add(new Edge(u, v, cost));
            }
        }
        
        int nEdges = candidateEdges.size();
        int minCost = Integer.MAX_VALUE;
        // Enumerate all subsets of candidate edges.
        // Only consider subsets that have at least (|subsetNodes| - 1) edges.
        int totalEdgeSubsets = 1 << nEdges;
        for (int mask = 0; mask < totalEdgeSubsets; mask++) {
            if (Integer.bitCount(mask) < subsetNodes.size() - 1)
                continue;
            
            List<Edge> selectedEdges = new ArrayList<>();
            int costSum = 0;
            for (int i = 0; i < nEdges; i++) {
                if (((mask >> i) & 1) == 1) {
                    Edge e = candidateEdges.get(i);
                    selectedEdges.add(e);
                    costSum += e.cost;
                }
            }
            // Check connectivity on these nodes with selected edges.
            if (!isConnected(subsetNodes, selectedEdges))
                continue;
            // For a single node, we already handled.
            if (subsetNodes.size() > 1 && !isTwoEdgeConnected(subsetNodes, selectedEdges))
                continue;
            minCost = Math.min(minCost, costSum);
        }
        return (minCost == Integer.MAX_VALUE) ? -1 : minCost;
    }
    
    // Check if the graph induced by selectedEdges on nodes (subsetNodes) is connected.
    private static boolean isConnected(List<Integer> subsetNodes, List<Edge> edges) {
        if (subsetNodes.isEmpty())
            return false;
        Set<Integer> visited = new HashSet<>();
        // Build graph as a map from node to list of neighbors.
        HashMap<Integer, List<Integer>> graph = new HashMap<>();
        for (Integer node : subsetNodes) {
            graph.put(node, new ArrayList<>());
        }
        for (Edge e : edges) {
            graph.get(e.u).add(e.v);
            graph.get(e.v).add(e.u);
        }
        // DFS starting from first node in subsetNodes.
        dfs(subsetNodes.get(0), graph, visited);
        return visited.containsAll(subsetNodes);
    }
    
    private static void dfs(int cur, HashMap<Integer, List<Integer>> graph, Set<Integer> visited) {
        visited.add(cur);
        for (int neighbor : graph.get(cur)) {
            if (!visited.contains(neighbor)) {
                dfs(neighbor, graph, visited);
            }
        }
    }
    
    // Check if the graph induced by selectedEdges on nodes (subsetNodes) is 2-edge-connected.
    // A graph is 2-edge-connected if removal of any single edge does not disconnect the graph.
    // Because candidate subgraphs are small, we use the simple method:
    // For each edge, temporarily remove it and check connectivity.
    private static boolean isTwoEdgeConnected(List<Integer> subsetNodes, List<Edge> edges) {
        // For every edge occurrence in the selected set, remove it and check connectivity.
        int size = edges.size();
        for (int removeIndex = 0; removeIndex < size; removeIndex++) {
            List<Edge> remainingEdges = new ArrayList<>();
            for (int j = 0; j < size; j++) {
                if (j != removeIndex) {
                    remainingEdges.add(edges.get(j));
                }
            }
            if (!isConnected(subsetNodes, remainingEdges)) {
                return false;
            }
        }
        return true;
    }
}