import java.util.*;

public class QosRouting {

    public static class Edge {
        public int source;
        public int destination;
        public int bandwidthCapacity;
        public int bandwidthUsage;
        public int latency;
        public double packetLossProbability;
        public int cost;

        public Edge(int source, int destination, int bandwidthCapacity, int bandwidthUsage, int latency, double packetLossProbability, int cost) {
            this.source = source;
            this.destination = destination;
            this.bandwidthCapacity = bandwidthCapacity;
            this.bandwidthUsage = bandwidthUsage;
            this.latency = latency;
            this.packetLossProbability = packetLossProbability;
            this.cost = cost;
        }
    }

    private static class State implements Comparable<State> {
        int node;
        int totalLatency;
        int totalCost;
        double productSuccess; // product of (1 - packetLossProbability) along the path
        List<Integer> path;

        State(int node, int totalLatency, int totalCost, double productSuccess, List<Integer> path) {
            this.node = node;
            this.totalLatency = totalLatency;
            this.totalCost = totalCost;
            this.productSuccess = productSuccess;
            this.path = path;
        }

        @Override
        public int compareTo(State other) {
            return Integer.compare(this.totalCost, other.totalCost);
        }
    }

    public static List<Integer> findOptimalPath(int numNodes, List<Edge> edges,
                                                  int sourceNode, int destinationNode,
                                                  int requiredBandwidth, int maxLatency,
                                                  double maxPacketLossProbability) {
        // Build adjacency list
        List<List<Edge>> graph = new ArrayList<>();
        for (int i = 0; i < numNodes; i++) {
            graph.add(new ArrayList<>());
        }
        for (Edge edge : edges) {
            graph.get(edge.source).add(edge);
        }

        // Minimum required cumulative success probability threshold
        double minSuccessProbability = 1.0 - maxPacketLossProbability;

        PriorityQueue<State> pq = new PriorityQueue<>();
        List<Integer> initialPath = new ArrayList<>();
        initialPath.add(sourceNode);
        State initialState = new State(sourceNode, 0, 0, 1.0, initialPath);
        pq.offer(initialState);

        // For pruning: for each node, maintain list of non-dominated states (by latency, cost, and productSuccess)
        List<List<State>> bestStates = new ArrayList<>();
        for (int i = 0; i < numNodes; i++) {
            bestStates.add(new ArrayList<>());
        }
        bestStates.get(sourceNode).add(initialState);

        // Special case when source and destination are the same.
        if (sourceNode == destinationNode) {
            return initialPath;
        }

        while (!pq.isEmpty()) {
            State curr = pq.poll();
            if (curr.node == destinationNode) {
                return curr.path;
            }

            // Explore neighbors
            for (Edge edge : graph.get(curr.node)) {
                // Check bandwidth constraint: available bandwidth must be >= requiredBandwidth.
                int availableBandwidth = edge.bandwidthCapacity - edge.bandwidthUsage;
                if (availableBandwidth < requiredBandwidth) {
                    continue;
                }

                int newLatency = curr.totalLatency + edge.latency;
                if (newLatency > maxLatency) {
                    continue;
                }

                double newProductSuccess = curr.productSuccess * (1.0 - edge.packetLossProbability);
                if (newProductSuccess < minSuccessProbability) {
                    continue;
                }

                int newCost = curr.totalCost + edge.cost;
                List<Integer> newPath = new ArrayList<>(curr.path);
                newPath.add(edge.destination);
                State newState = new State(edge.destination, newLatency, newCost, newProductSuccess, newPath);

                // Prune dominated states.
                boolean dominated = false;
                Iterator<State> it = bestStates.get(edge.destination).iterator();
                while (it.hasNext()) {
                    State existing = it.next();
                    if (existing.totalLatency <= newState.totalLatency && 
                        existing.productSuccess >= newState.productSuccess &&
                        existing.totalCost <= newState.totalCost) {
                        dominated = true;
                        break;
                    }
                    if (newState.totalLatency <= existing.totalLatency &&
                        newState.productSuccess >= existing.productSuccess &&
                        newState.totalCost <= existing.totalCost) {
                        it.remove();
                    }
                }
                if (dominated) {
                    continue;
                }
                bestStates.get(edge.destination).add(newState);
                pq.offer(newState);
            }
        }
        return new ArrayList<>();
    }
}