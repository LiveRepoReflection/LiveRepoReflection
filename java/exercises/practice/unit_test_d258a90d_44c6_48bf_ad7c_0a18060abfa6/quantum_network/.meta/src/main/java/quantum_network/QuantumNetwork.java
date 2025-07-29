package quantum_network;

import java.util.*;
import java.lang.Math;

public class QuantumNetwork {

    // Helper class to represent an edge in the graph.
    private static class Edge {
        int dest;
        double fidelity;
        double weight; // weight = -log(fidelity)
        
        Edge(int dest, double fidelity) {
            this.dest = dest;
            this.fidelity = fidelity;
            this.weight = -Math.log(fidelity);
        }
    }
    
    // Helper class for Dijkstra algorithm state.
    private static class NodeState {
        int node;
        double distance;
        
        NodeState(int node, double distance) {
            this.node = node;
            this.distance = distance;
        }
    }
    
    // Use Dijkstra algorithm with weights = -log(fidelity)
    // Returns a path from source to dest as a list of node indices, or an empty list if not reachable.
    private static List<Integer> dijkstra(int source, int dest, int N, List<double[]> channels) {
        // Build the graph as adjacency list.
        List<List<Edge>> graph = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            graph.add(new ArrayList<>());
        }
        for (double[] ch : channels) {
            int u = (int) ch[0];
            int v = (int) ch[1];
            double fidelity = ch[2];
            graph.get(u).add(new Edge(v, fidelity));
            graph.get(v).add(new Edge(u, fidelity));
        }
        
        double[] dist = new double[N];
        Arrays.fill(dist, Double.POSITIVE_INFINITY);
        int[] prev = new int[N];
        Arrays.fill(prev, -1);
        dist[source] = 0.0;
        
        PriorityQueue<NodeState> queue = new PriorityQueue<>(Comparator.comparingDouble(ns -> ns.distance));
        queue.offer(new NodeState(source, 0.0));
        
        boolean[] visited = new boolean[N];
        
        while (!queue.isEmpty()) {
            NodeState current = queue.poll();
            int u = current.node;
            if (visited[u]) {
                continue;
            }
            visited[u] = true;
            if (u == dest) {
                break;
            }
            for (Edge edge : graph.get(u)) {
                int v = edge.dest;
                double newDist = current.distance + edge.weight;
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    prev[v] = u;
                    queue.offer(new NodeState(v, newDist));
                }
            }
        }
        
        if (dist[dest] == Double.POSITIVE_INFINITY) {
            return new ArrayList<>();
        }
        
        List<Integer> path = new LinkedList<>();
        for (int at = dest; at != -1; at = prev[at]) {
            path.add(0, at);
        }
        return path;
    }
    
    // Calculate the fidelity of a path by multiplying the fidelities of the channels used.
    private static double pathFidelity(List<Integer> path, List<double[]> channels) {
        if (path.size() < 2) return 0.0;
        double prod = 1.0;
        // Build a map for quick lookup: unordered pair key -> fidelity
        Map<String, Double> map = new HashMap<>();
        for (double[] ch : channels) {
            int u = (int) ch[0];
            int v = (int) ch[1];
            String key = (u < v) ? (u + "_" + v) : (v + "_" + u);
            double f = ch[2];
            if (!map.containsKey(key) || f > map.get(key)) {
                map.put(key, f);
            }
        }
        for (int i = 0; i < path.size() - 1; i++) {
            int u = path.get(i);
            int v = path.get(i+1);
            String key = (u < v) ? (u + "_" + v) : (v + "_" + u);
            Double f = map.get(key);
            if (f == null) return 0.0;
            prod *= f;
        }
        return prod;
    }
    
    // Helper class to hold candidate information for a communication request.
    private static class RequestCandidate {
        int requestIndex;
        int source;
        int dest;
        List<Integer> path;
        double fidelity;
        
        RequestCandidate(int requestIndex, int source, int dest, List<Integer> path, double fidelity) {
            this.requestIndex = requestIndex;
            this.source = source;
            this.dest = dest;
            this.path = path;
            this.fidelity = fidelity;
        }
    }
    
    /**
     * Optimize the quantum network by assigning communication requests paths while respecting node capacities.
     *
     * @param N              Total number of nodes.
     * @param channels       List of channels, each represented by a double array {u, v, fidelity}.
     * @param requests       List of communication requests, each represented by an int array {source, destination}.
     * @param nodeCapacities Array of node capacities.
     * @return List of paths (each path is a list of integer node indices) assigned to each communication request.
     *         If a request cannot be satisfied, an empty list is returned for that request.
     */
    public static List<List<Integer>> optimizeNetwork(int N, List<double[]> channels, List<int[]> requests, int[] nodeCapacities) {
        List<List<Integer>> result = new ArrayList<>();
        int K = requests.size();
        for (int i = 0; i < K; i++) {
            result.add(new ArrayList<>());
        }
        
        int[] usage = new int[N]; // current usage of nodes
        
        List<RequestCandidate> candidates = new ArrayList<>();
        // For each request, compute the best possible path using Dijkstra.
        for (int i = 0; i < K; i++) {
            int source = requests.get(i)[0];
            int dest = requests.get(i)[1];
            List<Integer> path = dijkstra(source, dest, N, channels);
            if (path.isEmpty()) {
                candidates.add(new RequestCandidate(i, source, dest, path, -1.0));
            } else {
                double pathFid = pathFidelity(path, channels);
                candidates.add(new RequestCandidate(i, source, dest, path, pathFid));
            }
        }
        
        // Sort communication requests by descending order of fidelity candidate.
        candidates.sort((a, b) -> Double.compare(b.fidelity, a.fidelity));
        
        // Greedily assign requests if node capacities allow.
        for (RequestCandidate candidate : candidates) {
            if (candidate.path.isEmpty() || candidate.fidelity < 0) {
                continue;
            }
            boolean canAssign = true;
            for (int node : candidate.path) {
                if (usage[node] + 1 > nodeCapacities[node]) {
                    canAssign = false;
                    break;
                }
            }
            if (canAssign) {
                for (int node : candidate.path) {
                    usage[node]++;
                }
                result.set(candidate.requestIndex, candidate.path);
            }
            // If not assignable, the request remains with an empty path.
        }
        return result;
    }
}