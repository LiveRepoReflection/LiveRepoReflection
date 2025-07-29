import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

public class RoutePlanner {

    private final Map<Integer, List<Edge>> graph;

    public RoutePlanner() {
        this.graph = new HashMap<>();
    }

    public void addEdge(int from, int to, int length, int speedLimit) {
        Edge edge = new Edge(from, to, length, speedLimit);
        graph.computeIfAbsent(from, k -> new ArrayList<>()).add(edge);
        // Ensure destination node exists in graph
        graph.computeIfAbsent(to, k -> new ArrayList<>());
    }

    public void updateTraffic(TrafficUpdate update) {
        if (update.factor <= 0) {
            // Ignore invalid updates (non-positive congestion factor).
            return;
        }
        List<Edge> edges = graph.get(update.from);
        if (edges != null) {
            for (Edge edge : edges) {
                if (edge.to == update.to) {
                    synchronized (edge) {
                        edge.trafficUpdates.add(update);
                    }
                }
            }
        }
    }

    public List<Integer> findFastestRoute(int start, int end, int departureTime) {
        // Special case: start and end are the same.
        if (start == end) {
            List<Integer> route = new ArrayList<>();
            route.add(start);
            return route;
        }

        // Dijkstra's algorithm modified for time-dependent edges.
        Map<Integer, Double> arrivalTime = new HashMap<>();
        Map<Integer, Integer> parent = new HashMap<>();
        for (Integer node : graph.keySet()) {
            arrivalTime.put(node, Double.POSITIVE_INFINITY);
        }
        arrivalTime.put(start, (double) departureTime);

        // PriorityQueue entry: (current arrival time, node)
        PriorityQueue<NodeState> queue = new PriorityQueue<>();
        queue.add(new NodeState(start, departureTime));

        while (!queue.isEmpty()) {
            NodeState current = queue.poll();
            if (current.time > arrivalTime.get(current.node))
                continue;

            // Stop if destination reached.
            if (current.node == end) {
                return reconstructPath(parent, start, end);
            }

            List<Edge> neighbors = graph.get(current.node);
            if (neighbors == null)
                continue;

            for (Edge edge : neighbors) {
                double currTime = current.time;
                double travelTime = edge.getEffectiveTravelTime(currTime);
                double newArrival = currTime + travelTime;
                if (newArrival < arrivalTime.getOrDefault(edge.to, Double.POSITIVE_INFINITY)) {
                    arrivalTime.put(edge.to, newArrival);
                    parent.put(edge.to, current.node);
                    queue.add(new NodeState(edge.to, newArrival));
                }
            }
        }
        return null; // No route found.
    }

    private List<Integer> reconstructPath(Map<Integer, Integer> parent, int start, int end) {
        List<Integer> path = new ArrayList<>();
        int current = end;
        while (current != start) {
            path.add(0, current);
            if (!parent.containsKey(current)) {
                return null; // No valid path.
            }
            current = parent.get(current);
        }
        path.add(0, start);
        return path;
    }

    // Internal class representing an edge in the graph.
    private static class Edge {
        final int from;
        final int to;
        final int length; // in meters
        final int speedLimit; // in km/h
        final List<TrafficUpdate> trafficUpdates;

        Edge(int from, int to, int length, int speedLimit) {
            this.from = from;
            this.to = to;
            this.length = length;
            this.speedLimit = speedLimit;
            this.trafficUpdates = new ArrayList<>();
        }

        double getBaseTravelTime() {
            // Convert speedLimit from km/h to m/s: (speedLimit * 1000) / 3600
            double speedInMetersPerSecond = (speedLimit * 1000.0) / 3600.0;
            return length / speedInMetersPerSecond;
        }

        double getEffectiveTravelTime(double currentTime) {
            double factor = 1.0;
            synchronized (this) {
                for (TrafficUpdate update : trafficUpdates) {
                    if (currentTime >= update.startTime && currentTime <= update.endTime) {
                        factor = Math.max(factor, update.factor);
                    }
                }
            }
            return getBaseTravelTime() * factor;
        }
    }

    // Internal class representing a state in Dijkstra's algorithm.
    private static class NodeState implements Comparable<NodeState> {
        final int node;
        final double time;

        NodeState(int node, double time) {
            this.node = node;
            this.time = time;
        }

        @Override
        public int compareTo(NodeState other) {
            return Double.compare(this.time, other.time);
        }
    }
}