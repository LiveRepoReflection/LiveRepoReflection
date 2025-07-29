package route_optimizer;

import java.util.*;

public class Graph {
    private Map<String, List<Edge>> adj;

    public Graph() {
        this.adj = new HashMap<>();
    }

    public void addCity(String city) {
        adj.putIfAbsent(city, new ArrayList<>());
    }

    public void addEdge(String from, String to, double cost, int time) {
        if (!adj.containsKey(from)) {
            addCity(from);
        }
        if (!adj.containsKey(to)) {
            addCity(to);
        }
        adj.get(from).add(new Edge(to, cost, time));
    }

    public List<Edge> getNeighbors(String city) {
        return adj.getOrDefault(city, new ArrayList<>());
    }
    
    public boolean hasOutgoingEdges(String city) {
        List<Edge> edges = adj.get(city);
        return edges != null && !edges.isEmpty();
    }

    public Set<String> getCities() {
        return adj.keySet();
    }
}