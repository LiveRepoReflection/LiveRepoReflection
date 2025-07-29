import java.util.*;

public class NetworkRouting {
    // Graph represented as a mapping from a node to its neighbors and their corresponding Link
    private Map<Integer, Map<Integer, Link>> graph;
    // Global default weights used if no weights are provided in getOptimalPath
    private double[] defaultWeights;
    // Number of cost metrics, inferred from first link
    private int metricsCount;

    public NetworkRouting(List<Link> initialLinks, double[] defaultWeights) {
        this.graph = new HashMap<>();
        if (defaultWeights == null) {
            throw new IllegalArgumentException("Default weights cannot be null.");
        }
        this.defaultWeights = new double[defaultWeights.length];
        System.arraycopy(defaultWeights, 0, this.defaultWeights, 0, defaultWeights.length);
        // Initialize metricsCount based on defaultWeights length
        this.metricsCount = defaultWeights.length;
        // Add initial links
        if (initialLinks != null) {
            for (Link link : initialLinks) {
                // Validate that the link has the correct number of metrics
                if (link.costs.length != metricsCount) {
                    throw new IllegalArgumentException("Link cost metrics length mismatch with default weights.");
                }
                addLink(link.node1, link.node2, link.costs);
            }
        }
    }

    // Add a new bidirectional link in the network.
    public void addLink(int node1, int node2, int[] costs) {
        if (costs == null || costs.length != metricsCount) {
            throw new IllegalArgumentException("Invalid costs array.");
        }
        Link newLink = new Link(node1, node2, costs);
        // Update for node1
        graph.computeIfAbsent(node1, k -> new HashMap<>()).put(node2, newLink);
        // Update for node2
        graph.computeIfAbsent(node2, k -> new HashMap<>()).put(node1, newLink);
    }

    // Remove an existing bidirectional link from the network.
    public void removeLink(int node1, int node2) {
        if (graph.containsKey(node1)) {
            graph.get(node1).remove(node2);
        }
        if (graph.containsKey(node2)) {
            graph.get(node2).remove(node1);
        }
    }

    // Update the link cost between node1 and node2.
    public void changeLinkCost(int node1, int node2, int[] newCosts) {
        if (newCosts == null || newCosts.length != metricsCount) {
            throw new IllegalArgumentException("Invalid newCosts array.");
        }
        if (graph.containsKey(node1) && graph.get(node1).containsKey(node2)) {
            // Update the Link object in both directions.
            Link link = graph.get(node1).get(node2);
            link.costs = new int[newCosts.length];
            System.arraycopy(newCosts, 0, link.costs, 0, newCosts.length);
        }
    }

    // Update the global default weights.
    public void updateWeights(double[] newWeights) {
        if (newWeights == null || newWeights.length != metricsCount) {
            throw new IllegalArgumentException("Invalid weights array.");
        }
        this.defaultWeights = new double[newWeights.length];
        System.arraycopy(newWeights, 0, this.defaultWeights, 0, newWeights.length);
    }

    // Get the optimal (lowest-cost) path from source to destination using provided weights.
    // If weights is null, use the default weights.
    public List<Integer> getOptimalPath(int source, int destination, double[] weights) {
        double[] usedWeights = weights;
        if (usedWeights == null) {
            usedWeights = this.defaultWeights;
        } else if (usedWeights.length != metricsCount) {
            throw new IllegalArgumentException("Weights array length must match number of cost metrics.");
        }
        
        // Dijkstra's algorithm for weighted shortest path.
        Map<Integer, Double> dist = new HashMap<>();
        Map<Integer, Integer> prev = new HashMap<>();
        PriorityQueue<NodeEntry> pq = new PriorityQueue<>(Comparator.comparingDouble(ne -> ne.cost));

        // Initialize distances: source = 0, all others = infinity.
        dist.put(source, 0.0);
        pq.offer(new NodeEntry(source, 0.0));

        while (!pq.isEmpty()) {
            NodeEntry current = pq.poll();
            int currentNode = current.node;
            double currentCost = current.cost;
            
            // If we have reached destination, no need to process further.
            if (currentNode == destination) {
                break;
            }
            
            // Skip outdated queue entries.
            if (currentCost > dist.getOrDefault(currentNode, Double.MAX_VALUE)) {
                continue;
            }
            
            Map<Integer, Link> neighbors = graph.getOrDefault(currentNode, Collections.emptyMap());
            for (Map.Entry<Integer, Link> entry : neighbors.entrySet()) {
                int neighbor = entry.getKey();
                Link edge = entry.getValue();
                double weightCost = edge.getWeightedCost(usedWeights);
                double newDistance = currentCost + weightCost;
                if (newDistance < dist.getOrDefault(neighbor, Double.MAX_VALUE)) {
                    dist.put(neighbor, newDistance);
                    prev.put(neighbor, currentNode);
                    pq.offer(new NodeEntry(neighbor, newDistance));
                }
            }
        }

        // Reconstruct path from source to destination.
        if (!dist.containsKey(destination)) {
            return Collections.emptyList();
        }
        List<Integer> path = new LinkedList<>();
        for (Integer at = destination; at != null; at = prev.get(at)) {
            path.add(0, at);
        }
        return path;
    }

    // Helper class for PriorityQueue in Dijkstra's algorithm.
    private static class NodeEntry {
        int node;
        double cost;
        
        NodeEntry(int node, double cost) {
            this.node = node;
            this.cost = cost;
        }
    }
}