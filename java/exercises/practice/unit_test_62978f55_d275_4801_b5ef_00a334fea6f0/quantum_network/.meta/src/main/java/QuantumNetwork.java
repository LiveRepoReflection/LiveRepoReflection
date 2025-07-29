import java.util.*;

public class QuantumNetwork {
    private final int n;
    private final List<Edge>[] adjacencyList;
    private final int source;
    private final int destination;
    private final int minFidelity;
    private static final int INF = Integer.MAX_VALUE;

    private static class Edge {
        int to;
        int cost;
        int fidelity;

        Edge(int to, int cost, int fidelity) {
            this.to = to;
            this.cost = cost;
            this.fidelity = fidelity;
        }
    }

    private static class State implements Comparable<State> {
        int node;
        int cost;
        long fidelity;

        State(int node, int cost, long fidelity) {
            this.node = node;
            this.cost = cost;
            this.fidelity = fidelity;
        }

        @Override
        public int compareTo(State other) {
            return Integer.compare(this.cost, other.cost);
        }
    }

    @SuppressWarnings("unchecked")
    public QuantumNetwork(int n, int[][] edges, int source, int destination, int minFidelity) {
        this.n = n;
        this.source = source;
        this.destination = destination;
        this.minFidelity = minFidelity;
        
        // Initialize adjacency list
        this.adjacencyList = new List[n];
        for (int i = 0; i < n; i++) {
            adjacencyList[i] = new ArrayList<>();
        }

        // Build graph
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int cost = edge[2];
            int fidelity = edge[3];
            
            // Add edges in both directions as the graph is undirected
            adjacencyList[u].add(new Edge(v, cost, fidelity));
            adjacencyList[v].add(new Edge(u, cost, fidelity));
        }
    }

    public int findMinCostPath() {
        // Handle special case where source and destination are the same
        if (source == destination) {
            return 0;
        }

        // Use priority queue for Dijkstra's algorithm
        PriorityQueue<State> pq = new PriorityQueue<>();
        // Keep track of best cost for each node at each fidelity level
        Map<String, Integer> visited = new HashMap<>();

        // Start from source with 0 cost and 100% fidelity
        pq.offer(new State(source, 0, 100));

        while (!pq.isEmpty()) {
            State current = pq.poll();
            
            // If we reached destination with sufficient fidelity, return cost
            if (current.node == destination && current.fidelity >= minFidelity) {
                return current.cost;
            }

            // Create state key for memoization
            String stateKey = current.node + "," + current.fidelity;
            
            // Skip if we've seen this state with a better cost
            if (visited.containsKey(stateKey) && visited.get(stateKey) <= current.cost) {
                continue;
            }
            
            visited.put(stateKey, current.cost);

            // Explore all neighbors
            for (Edge edge : adjacencyList[current.node]) {
                // Calculate new fidelity as percentage
                long newFidelity = (current.fidelity * edge.fidelity) / 100;
                
                // Skip if fidelity becomes too low
                if (newFidelity < minFidelity) {
                    continue;
                }

                // Calculate new cost
                int newCost = current.cost + edge.cost;
                
                // Create new state key for neighbor
                String nextStateKey = edge.to + "," + newFidelity;
                
                // Add to queue if this is a better path or new state
                if (!visited.containsKey(nextStateKey) || visited.get(nextStateKey) > newCost) {
                    pq.offer(new State(edge.to, newCost, newFidelity));
                }
            }
        }

        // No valid path found
        return -1;
    }
}