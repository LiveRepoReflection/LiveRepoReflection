import java.util.*;

public class MultiShortestPath {

    public static class Edge {
        public int from;
        public int to;
        public int cost;
        
        public Edge(int from, int to, int cost) {
            this.from = from;
            this.to = to;
            this.cost = cost;
        }
    }
    
    public static int[] findMinCosts(int n, List<Edge> edges, List<Integer> sources) {
        List<List<Edge>> graph = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        for (Edge e : edges) {
            graph.get(e.from).add(e);
        }
        
        int[] dist = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a.cost));
        for (int src : sources) {
            if (src >= 0 && src < n) {
                dist[src] = 0;
                pq.offer(new Node(src, 0));
            }
        }
        
        while (!pq.isEmpty()) {
            Node current = pq.poll();
            if (current.cost > dist[current.vertex]) {
                continue;
            }
            
            for (Edge edge : graph.get(current.vertex)) {
                int next = edge.to;
                int newCost = current.cost + edge.cost;
                if (newCost < dist[next]) {
                    dist[next] = newCost;
                    pq.offer(new Node(next, newCost));
                }
            }
        }
        
        for (int i = 0; i < n; i++) {
            if (dist[i] == Integer.MAX_VALUE) {
                dist[i] = -1;
            }
        }
        
        return dist;
    }
    
    private static class Node {
        int vertex;
        int cost;
        
        Node(int vertex, int cost) {
            this.vertex = vertex;
            this.cost = cost;
        }
    }
}