import java.util.*;

public class UltraSpeedLogistics {
    private static class Edge {
        int source, destination, time;
        Edge(int source, int destination, int time) {
            this.source = source;
            this.destination = destination;
            this.time = time;
        }
    }

    private static class State implements Comparable<State> {
        int node;
        double time;
        List<Integer> path;
        Set<String> visitedEdges;

        State(int node, double time, List<Integer> path, Set<String> visitedEdges) {
            this.node = node;
            this.time = time;
            this.path = new ArrayList<>(path);
            this.visitedEdges = new HashSet<>(visitedEdges);
        }

        @Override
        public int compareTo(State other) {
            int timeCompare = Double.compare(this.time, other.time);
            if (timeCompare != 0) return timeCompare;
            return Integer.compare(this.path.size(), other.path.size());
        }
    }

    private Map<Integer, List<Edge>> graph;
    private Map<String, List<int[]>> trafficEvents;
    private long memoryUsed;
    private final long MEMORY_PER_STATE = 200; // Approximate memory per State object in bytes

    public List<List<List<Integer>>> findEfficientRoutes(
            List<int[]> edges,
            List<int[]> requests,
            List<int[]> trafficEvents,
            int k,
            int cacheLimit
    ) {
        initializeGraph(edges);
        initializeTrafficEvents(trafficEvents);
        List<List<List<Integer>>> result = new ArrayList<>();

        for (int[] request : requests) {
            result.add(findKShortestPaths(
                request[0], // start
                request[1], // end
                request[2], // deadline
                k,
                cacheLimit
            ));
        }

        return result;
    }

    private void initializeGraph(List<int[]> edges) {
        graph = new HashMap<>();
        for (int[] edge : edges) {
            graph.computeIfAbsent(edge[0], k -> new ArrayList<>())
                 .add(new Edge(edge[0], edge[1], edge[2]));
        }
    }

    private void initializeTrafficEvents(List<int[]> events) {
        trafficEvents = new HashMap<>();
        for (int[] event : events) {
            String key = event[0] + "," + event[1];
            trafficEvents.computeIfAbsent(key, k -> new ArrayList<>())
                        .add(new int[]{event[2], event[3], event[4]});
        }
    }

    private double calculateEdgeTime(Edge edge, double currentTime, Set<String> visitedEdges) {
        String edgeKey = edge.source + "," + edge.destination;
        if (visitedEdges.contains(edgeKey)) {
            return edge.time;
        }

        double maxIncrease = 0;
        if (trafficEvents.containsKey(edgeKey)) {
            for (int[] event : trafficEvents.get(edgeKey)) {
                if (currentTime >= event[0] && currentTime <= event[1]) {
                    maxIncrease = Math.max(maxIncrease, event[2]);
                }
            }
        }

        return edge.time * (1 + maxIncrease / 100.0);
    }

    private List<List<Integer>> findKShortestPaths(
            int start,
            int end,
            int deadline,
            int k,
            int cacheLimit
    ) {
        memoryUsed = 0;
        PriorityQueue<State> pq = new PriorityQueue<>();
        List<List<Integer>> result = new ArrayList<>();
        Set<String> visited = new HashSet<>();

        // Initialize start state
        List<Integer> initialPath = new ArrayList<>();
        initialPath.add(start);
        pq.offer(new State(start, 0, initialPath, new HashSet<>()));
        updateMemoryUsage(1);

        while (!pq.isEmpty() && result.size() < k) {
            State current = pq.poll();
            updateMemoryUsage(-1);

            if (current.node == end) {
                String pathKey = current.path.toString();
                if (!visited.contains(pathKey) && current.time <= deadline) {
                    result.add(current.path);
                    visited.add(pathKey);
                    continue;
                }
            }

            if (!graph.containsKey(current.node)) continue;

            for (Edge edge : graph.get(current.node)) {
                double newTime = current.time + calculateEdgeTime(edge, current.time, current.visitedEdges);
                if (newTime > deadline) continue;

                List<Integer> newPath = new ArrayList<>(current.path);
                newPath.add(edge.destination);

                Set<String> newVisitedEdges = new HashSet<>(current.visitedEdges);
                newVisitedEdges.add(edge.source + "," + edge.destination);

                State newState = new State(edge.destination, newTime, newPath, newVisitedEdges);
                pq.offer(newState);
                updateMemoryUsage(1);

                // Check cache limit
                if (memoryUsed > cacheLimit) {
                    throw new RuntimeException("Cache limit exceeded");
                }
            }
        }

        return result;
    }

    private void updateMemoryUsage(int stateCount) {
        memoryUsed += stateCount * MEMORY_PER_STATE;
    }
}