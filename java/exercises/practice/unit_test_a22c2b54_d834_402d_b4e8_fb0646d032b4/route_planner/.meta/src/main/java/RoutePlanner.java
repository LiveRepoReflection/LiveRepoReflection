package route_planner;

import java.util.*;

public class RoutePlanner {
    private final int numNodes;
    private final List<List<Edge>> graph;

    public RoutePlanner(int numNodes) {
        this.numNodes = numNodes;
        graph = new ArrayList<>(numNodes);
        for (int i = 0; i < numNodes; i++) {
            graph.add(new ArrayList<>());
        }
    }

    public void addEdge(int source, int destination, int defaultTraversalTime) {
        Edge edge = new Edge(source, destination, defaultTraversalTime);
        graph.get(source).add(edge);
    }

    public void updateRoute(int source, int destination, int timestamp, int newTraversalTime) {
        List<Edge> edges = graph.get(source);
        for (Edge edge : edges) {
            if (edge.destination == destination) {
                edge.addUpdate(timestamp, newTraversalTime);
            }
        }
    }

    public int getOptimalDeliveryRoute(int startLocation, int endLocation, int startTime) {
        int[] distances = new int[numNodes];
        Arrays.fill(distances, Integer.MAX_VALUE);
        distances[startLocation] = 0;

        PriorityQueue<Node> minHeap = new PriorityQueue<>(Comparator.comparingInt(n -> n.distance));
        minHeap.offer(new Node(startLocation, 0));

        while (!minHeap.isEmpty()) {
            Node current = minHeap.poll();

            if (current.distance > distances[current.id]) {
                continue;
            }

            if (current.id == endLocation) {
                return current.distance;
            }

            List<Edge> edges = graph.get(current.id);
            for (Edge edge : edges) {
                int effectiveWeight = edge.getEffectiveWeight(startTime);
                // Skip the edge if its effective weight is Integer.MAX_VALUE
                if (effectiveWeight == Integer.MAX_VALUE) {
                    continue;
                }
                if ((current.distance != Integer.MAX_VALUE) && (current.distance + effectiveWeight < distances[edge.destination])) {
                    distances[edge.destination] = current.distance + effectiveWeight;
                    minHeap.offer(new Node(edge.destination, distances[edge.destination]));
                }
            }
        }

        return distances[endLocation] == Integer.MAX_VALUE ? -1 : distances[endLocation];
    }

    private static class Node {
        int id;
        int distance;

        Node(int id, int distance) {
            this.id = id;
            this.distance = distance;
        }
    }

    private static class Edge {
        int source;
        int destination;
        int defaultWeight;
        // TreeMap with key: timestamp, value: updated traversal time.
        private final TreeMap<Integer, Integer> updates;

        Edge(int source, int destination, int defaultWeight) {
            this.source = source;
            this.destination = destination;
            this.defaultWeight = defaultWeight;
            this.updates = new TreeMap<>();
        }

        void addUpdate(int timestamp, int newTraversalTime) {
            updates.put(timestamp, newTraversalTime);
        }

        int getEffectiveWeight(int queryTime) {
            Map.Entry<Integer, Integer> entry = updates.floorEntry(queryTime);
            if (entry != null) {
                return entry.getValue();
            }
            return defaultWeight;
        }
    }
}