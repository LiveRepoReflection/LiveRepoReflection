import java.util.*;

public class OptimalNetworkPlacement {

    public List<List<Integer>> designNetwork(int numDataCenters, int[][] distances, int minConnectivity, int maxLatency) {
        // Initialize the candidate set as all nodes.
        Set<Integer> candidateNodes = new HashSet<>();
        for (int i = 0; i < numDataCenters; i++) {
            candidateNodes.add(i);
        }
        
        NetworkSolution bestSolution = buildNetworkForSubset(candidateNodes, distances, minConnectivity, maxLatency);
        if (bestSolution == null) {
            return new ArrayList<>();
        }
        
        // Attempt to reduce the number of nodes selected by trying to remove nodes one by one.
        boolean improvement = true;
        while (improvement) {
            improvement = false;
            // Convert current candidate set to list to iterate over a copy.
            List<Integer> currentNodes = new ArrayList<>(candidateNodes);
            // Try removing each node and check if we still get a valid network.
            for (int node : currentNodes) {
                Set<Integer> newCandidateNodes = new HashSet<>(candidateNodes);
                newCandidateNodes.remove(node);
                // It's possible that a network with one node is valid if minConnectivity==0,
                // but in our setting connectivity generally requires at least two nodes.
                if (newCandidateNodes.size() < 1) {
                    continue;
                }
                NetworkSolution candidateSolution = buildNetworkForSubset(newCandidateNodes, distances, minConnectivity, maxLatency);
                if (candidateSolution != null) {
                    // We found a valid network with fewer nodes.
                    candidateNodes = newCandidateNodes;
                    bestSolution = candidateSolution;
                    improvement = true;
                    break;
                }
            }
        }
        
        return bestSolution.network;
    }
    
    // A helper class to store a network solution and its total latency.
    private static class NetworkSolution {
        List<List<Integer>> network;
        int totalLatency;
        
        NetworkSolution(List<List<Integer>> network, int totalLatency) {
            this.network = network;
            this.totalLatency = totalLatency;
        }
    }
    
    // Build a network for the given subset of nodes S that satisfies:
    // 1. The network is connected (using a minimum spanning tree).
    // 2. Every node in S has degree at least minConnectivity (by adding extra edges if needed).
    // 3. The total latency does not exceed maxLatency.
    // Returns a NetworkSolution if possible or null if no valid network can be found.
    private NetworkSolution buildNetworkForSubset(Set<Integer> S, int[][] distances, int minConnectivity, int maxLatency) {
        // The set S must have at least one node.
        if (S.isEmpty()) {
            return null;
        }
        
        List<Integer> nodes = new ArrayList<>(S);
        // Use a set to store edges in canonical form "minIndex_maxIndex"
        Set<String> addedEdgesSet = new HashSet<>();
        List<List<Integer>> networkEdges = new ArrayList<>();
        int totalCost = 0;
        
        // Build Minimum Spanning Tree (MST) among nodes in S using Prim's algorithm.
        Set<Integer> inTree = new HashSet<>();
        // Choose an arbitrary start node.
        inTree.add(nodes.get(0));
        
        // A priority queue for candidate edges: [cost, u, v] where u in tree, v not in tree.
        PriorityQueue<Edge> edgeQueue = new PriorityQueue<>(Comparator.comparingInt(e -> e.weight));
        
        for (int v : S) {
            if (!inTree.contains(v)) {
                int u = nodes.get(0);
                int cost = distances[u][v];
                edgeQueue.offer(new Edge(u, v, cost));
            }
        }
        
        while (inTree.size() < S.size() && !edgeQueue.isEmpty()) {
            Edge edge = edgeQueue.poll();
            if (inTree.contains(edge.v)) {
                continue;
            }
            // Add edge to MST.
            String key = canonicalKey(edge.u, edge.v);
            addedEdgesSet.add(key);
            networkEdges.add(Arrays.asList(edge.u, edge.v));
            totalCost += edge.weight;
            inTree.add(edge.v);
            // Add new candidate edges from the newly added node.
            for (int w : S) {
                if (!inTree.contains(w)) {
                    edgeQueue.offer(new Edge(edge.v, w, distances[edge.v][w]));
                }
            }
        }
        
        // If not all nodes from S are connected, return null.
        if (inTree.size() != S.size()) {
            return null;
        }
        
        // Compute current degrees.
        Map<Integer, Integer> degreeMap = computeDegrees(networkEdges);
        
        // While there are nodes that do not meet minConnectivity, add extra edges.
        while (existsDeficientNode(S, degreeMap, minConnectivity)) {
            Edge bestCandidate = null;
            // Search for the smallest edge (i,j) that is not already in network,
            // and that helps at least one deficient node.
            for (int i : S) {
                for (int j : S) {
                    if (i >= j) {
                        continue;
                    }
                    // Skip if edge is already added.
                    String key = canonicalKey(i, j);
                    if (addedEdgesSet.contains(key)) {
                        continue;
                    }
                    // Check if at least one endpoint is deficient.
                    int degI = degreeMap.getOrDefault(i, 0);
                    int degJ = degreeMap.getOrDefault(j, 0);
                    if (degI < minConnectivity || degJ < minConnectivity) {
                        int cost = distances[i][j];
                        if (bestCandidate == null || cost < bestCandidate.weight) {
                            bestCandidate = new Edge(i, j, cost);
                        }
                    }
                }
            }
            if (bestCandidate == null) {
                // No available edge can help satisfy the connectivity requirement.
                return null;
            }
            // Add the selected extra edge.
            String edgeKey = canonicalKey(bestCandidate.u, bestCandidate.v);
            addedEdgesSet.add(edgeKey);
            networkEdges.add(Arrays.asList(bestCandidate.u, bestCandidate.v));
            totalCost += bestCandidate.weight;
            // Update degrees.
            degreeMap.put(bestCandidate.u, degreeMap.getOrDefault(bestCandidate.u, 0) + 1);
            degreeMap.put(bestCandidate.v, degreeMap.getOrDefault(bestCandidate.v, 0) + 1);
        }
        
        // After adding extra edges, check if the totalCost is within latency limit.
        if (totalCost > maxLatency) {
            return null;
        }
        
        return new NetworkSolution(networkEdges, totalCost);
    }
    
    // Helper method: returns the canonical key for an edge between u and v.
    private String canonicalKey(int u, int v) {
        if (u < v) {
            return u + "_" + v;
        } else {
            return v + "_" + u;
        }
    }
    
    // Helper method: checks if there exists any node in S with degree less than minConnectivity.
    private boolean existsDeficientNode(Set<Integer> S, Map<Integer, Integer> degreeMap, int minConnectivity) {
        for (int node : S) {
            if (degreeMap.getOrDefault(node, 0) < minConnectivity) {
                return true;
            }
        }
        return false;
    }
    
    // Helper method: computes degrees from a list of edges.
    private Map<Integer, Integer> computeDegrees(List<List<Integer>> edges) {
        Map<Integer, Integer> degreeMap = new HashMap<>();
        for (List<Integer> edge : edges) {
            int u = edge.get(0);
            int v = edge.get(1);
            degreeMap.put(u, degreeMap.getOrDefault(u, 0) + 1);
            degreeMap.put(v, degreeMap.getOrDefault(v, 0) + 1);
        }
        return degreeMap;
    }
    
    // Helper class to represent an edge.
    private static class Edge {
        int u;
        int v;
        int weight;
        
        Edge(int u, int v, int weight) {
            this.u = u;
            this.v = v;
            this.weight = weight;
        }
    }
}