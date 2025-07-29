import java.util.*;

public class NetworkRouting {
    private final Map<Integer, List<NodeEdge>> graph;
    private Map<Integer, Integer> serverCapacities;
    private final Map<String, List<Integer>> contentLocation;

    public NetworkRouting(List<Edge> edges, Map<Integer, Integer> serverCapacities, Map<String, List<Integer>> contentLocation) {
        this.serverCapacities = new HashMap<>(serverCapacities);
        this.contentLocation = new HashMap<>(contentLocation);
        this.graph = new HashMap<>();
        buildGraph(edges);
    }

    private void buildGraph(List<Edge> edges) {
        for (Edge edge : edges) {
            graph.computeIfAbsent(edge.getServer1(), k -> new ArrayList<>())
                 .add(new NodeEdge(edge.getServer2(), edge.getLatency()));
            graph.computeIfAbsent(edge.getServer2(), k -> new ArrayList<>())
                 .add(new NodeEdge(edge.getServer1(), edge.getLatency()));
        }
    }

    public void updateServerCapacities(Map<Integer, Integer> newCapacities) {
        this.serverCapacities = new HashMap<>(newCapacities);
    }

    public List<RoutingDecision> routeRequests(List<ContentRequest> requests) {
        List<RoutingDecision> decisions = new ArrayList<>();
        for (int i = 0; i < requests.size(); i++) {
            ContentRequest request = requests.get(i);
            String contentId = request.getContentId();
            if (!contentLocation.containsKey(contentId)) {
                decisions.add(new RoutingDecision(i, -1, "dropped"));
                continue;
            }
            List<Integer> candidateServers = contentLocation.get(contentId);
            Map<Integer, Integer> distances = dijkstra(request.getUserLocation());

            int bestServer = -1;
            int bestLatency = Integer.MAX_VALUE;
            for (int candidate : candidateServers) {
                if (!distances.containsKey(candidate)) continue;
                int latency = distances.get(candidate);
                if (latency < bestLatency && serverCapacities.getOrDefault(candidate, 0) > 0) {
                    bestLatency = latency;
                    bestServer = candidate;
                }
            }
            if (bestServer == -1) {
                decisions.add(new RoutingDecision(i, -1, "dropped"));
            } else {
                serverCapacities.put(bestServer, serverCapacities.get(bestServer) - 1);
                decisions.add(new RoutingDecision(i, bestServer, "served"));
            }
        }
        return decisions;
    }

    private Map<Integer, Integer> dijkstra(int source) {
        Map<Integer, Integer> distances = new HashMap<>();
        PriorityQueue<Pair> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a.latency));
        distances.put(source, 0);
        pq.offer(new Pair(source, 0));
        while (!pq.isEmpty()) {
            Pair current = pq.poll();
            if (current.latency > distances.get(current.server)) {
                continue;
            }
            List<NodeEdge> neighbors = graph.getOrDefault(current.server, new ArrayList<>());
            for (NodeEdge neighbor : neighbors) {
                int newLatency = current.latency + neighbor.latency;
                if (newLatency < distances.getOrDefault(neighbor.server, Integer.MAX_VALUE)) {
                    distances.put(neighbor.server, newLatency);
                    pq.offer(new Pair(neighbor.server, newLatency));
                }
            }
        }
        return distances;
    }

    private static class NodeEdge {
        int server;
        int latency;

        NodeEdge(int server, int latency) {
            this.server = server;
            this.latency = latency;
        }
    }

    private static class Pair {
        int server;
        int latency;

        Pair(int server, int latency) {
            this.server = server;
            this.latency = latency;
        }
    }
}