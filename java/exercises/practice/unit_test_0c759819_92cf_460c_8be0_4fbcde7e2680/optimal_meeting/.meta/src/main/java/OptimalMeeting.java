import java.util.*;

public class OptimalMeeting {

    static class Edge {
        int to;
        int weight;

        Edge(int to, int weight) {
            this.to = to;
            this.weight = weight;
        }
    }

    public int findOptimalMeetingPoint(int n, int[][] edges, int[] employeeLocations) {
        // Build the graph as an adjacency list.
        List<List<Edge>> graph = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            graph.get(u).add(new Edge(v, w));
            graph.get(v).add(new Edge(u, w));
        }

        // For each node, store the maximal distance from any employee.
        int[] maxDistance = new int[n];
        Arrays.fill(maxDistance, 0);

        // Run Dijkstra from each employee's location.
        for (int start : employeeLocations) {
            int[] dist = dijkstra(n, graph, start);
            for (int i = 0; i < n; i++) {
                // Update the maximum distance encountered for node i.
                if (dist[i] > maxDistance[i]) {
                    maxDistance[i] = dist[i];
                }
            }
        }

        // Choose the node with the minimum maximum distance.
        int optimalNode = -1;
        int optimalVal = Integer.MAX_VALUE;
        for (int i = 0; i < n; i++) {
            if (maxDistance[i] < optimalVal) {
                optimalVal = maxDistance[i];
                optimalNode = i;
            }
        }
        return optimalNode;
    }

    private int[] dijkstra(int n, List<List<Edge>> graph, int source) {
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        dist[source] = 0;

        PriorityQueue<Node> minHeap = new PriorityQueue<>((a, b) -> Integer.compare(a.dist, b.dist));
        minHeap.offer(new Node(source, 0));

        while (!minHeap.isEmpty()) {
            Node current = minHeap.poll();
            int u = current.vertex;
            int currentDist = current.dist;
            if (currentDist > dist[u]) {
                continue;
            }
            for (Edge edge : graph.get(u)) {
                int v = edge.to;
                int weight = edge.weight;
                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    minHeap.offer(new Node(v, dist[v]));
                }
            }
        }
        return dist;
    }

    static class Node {
        int vertex;
        int dist;

        Node(int vertex, int dist) {
            this.vertex = vertex;
            this.dist = dist;
        }
    }
}