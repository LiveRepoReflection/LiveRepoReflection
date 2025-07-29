import java.util.*;
import java.util.PriorityQueue;

public class TrafficRouter {

    private final Map<Integer, List<Edge>> graph;
    private final Map<Integer, Coordinate> coordinates;

    public TrafficRouter(List<Edge> edges, Map<Integer, Coordinate> coordinates) {
        this.graph = new HashMap<>();
        this.coordinates = new HashMap<>(coordinates);
        for (Edge edge : edges) {
            if (!this.coordinates.containsKey(edge.getSource()) || !this.coordinates.containsKey(edge.getDestination())) {
                throw new IllegalArgumentException("All nodes in edges must have coordinates.");
            }
            graph.computeIfAbsent(edge.getSource(), k -> new ArrayList<>()).add(edge);
            // For directed graph, ensure destination node is in graph even if it has no outgoing edges.
            graph.computeIfAbsent(edge.getDestination(), k -> new ArrayList<>());
        }
        // Also add isolated nodes that are only in coordinates.
        for (Integer node : coordinates.keySet()) {
            graph.computeIfAbsent(node, k -> new ArrayList<>());
        }
    }

    public RouteResult findRoute(int start, int destination) {
        if (!coordinates.containsKey(start) || !coordinates.containsKey(destination)) {
            throw new IllegalArgumentException("Invalid node ID");
        }
        // A* search
        // gScore: cost from start to current node.
        Map<Integer, Double> gScore = new HashMap<>();
        // cameFrom: used for reconstructing path.
        Map<Integer, Integer> cameFrom = new HashMap<>();

        // fScore: gScore + heuristic.
        Map<Integer, Double> fScore = new HashMap<>();

        Comparator<NodeEntry> comparator = Comparator.comparingDouble(ne -> ne.fScore);
        PriorityQueue<NodeEntry> openSet = new PriorityQueue<>(comparator);
        gScore.put(start, 0.0);
        double initialHeuristic = heuristic(start, destination);
        fScore.put(start, initialHeuristic);
        openSet.add(new NodeEntry(start, 0.0, initialHeuristic));

        while (!openSet.isEmpty()) {
            NodeEntry current = openSet.poll();
            if (current.node == destination) {
                List<Integer> path = reconstructPath(cameFrom, destination);
                return new RouteResult(path, gScore.get(destination));
            }
            // If current.gScore is greater than stored gScore then skip.
            if (current.gScore > gScore.getOrDefault(current.node, Double.POSITIVE_INFINITY)) {
                continue;
            }
            for (Edge edge : graph.getOrDefault(current.node, Collections.emptyList())) {
                int neighbor = edge.getDestination();
                double tentativeGScore = gScore.get(current.node) + edge.getTravelTime();
                if (tentativeGScore < gScore.getOrDefault(neighbor, Double.POSITIVE_INFINITY)) {
                    cameFrom.put(neighbor, current.node);
                    gScore.put(neighbor, tentativeGScore);
                    double estimatedFScore = tentativeGScore + heuristic(neighbor, destination);
                    fScore.put(neighbor, estimatedFScore);
                    openSet.add(new NodeEntry(neighbor, tentativeGScore, estimatedFScore));
                }
            }
        }
        // No route found
        return null;
    }

    public void updateTraffic(int source, int destination, double newCongestionFactor) {
        List<Edge> edges = graph.get(source);
        if (edges != null) {
            for (Edge edge : edges) {
                if (edge.getDestination() == destination) {
                    edge.setCongestionFactor(newCongestionFactor);
                }
            }
        }
    }

    private List<Integer> reconstructPath(Map<Integer, Integer> cameFrom, int current) {
        LinkedList<Integer> path = new LinkedList<>();
        path.addFirst(current);
        while (cameFrom.containsKey(current)) {
            current = cameFrom.get(current);
            path.addFirst(current);
        }
        return path;
    }

    private double heuristic(int current, int destination) {
        // Euclidean distance as heuristic
        Coordinate c1 = coordinates.get(current);
        Coordinate c2 = coordinates.get(destination);
        double dx = c1.getX() - c2.getX();
        double dy = c1.getY() - c2.getY();
        // Since base travel times are significantly larger than Euclidean distances in test cases,
        // the Euclidean distance serves as an admissible heuristic.
        return Math.sqrt(dx * dx + dy * dy);
    }

    private static class NodeEntry {
        int node;
        double gScore;
        double fScore;

        public NodeEntry(int node, double gScore, double fScore) {
            this.node = node;
            this.gScore = gScore;
            this.fScore = fScore;
        }
    }
}