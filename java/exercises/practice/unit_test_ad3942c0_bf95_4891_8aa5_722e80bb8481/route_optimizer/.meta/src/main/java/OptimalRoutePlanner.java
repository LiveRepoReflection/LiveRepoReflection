package route_optimizer;

import java.util.*;

public class OptimalRoutePlanner {

    public List<Route> planRoutes(Graph graph, Map<String, Integer> demand, String depot, int vehicleCapacity, int maxDuration, double costMultiplier) {
        if (!graph.hasOutgoingEdges(depot)) {
            throw new IllegalArgumentException("Depot has no outgoing edges");
        }
        
        List<Route> routes = new ArrayList<>();

        // For every city with positive demand, plan trips.
        for (String city : demand.keySet()) {
            int required = demand.get(city);
            if (required <= 0) continue; // Skip cities with zero or negative demand

            // Compute shortest route from depot to city
            Pair outbound = dijkstra(graph, depot, city);
            // Compute shortest route from city to depot
            Pair inbound = dijkstra(graph, city, depot);

            int roundTripTime = outbound.time + inbound.time;
            if (roundTripTime > maxDuration) {
                throw new IllegalArgumentException("No feasible route");
            }

            // Split deliveries if necessary based on vehicle capacity
            while (required > 0) {
                int delivered = Math.min(vehicleCapacity, required);
                int totalTime = roundTripTime;
                double totalCost = (outbound.cost + inbound.cost) * costMultiplier;
                List<String> citySequence = new ArrayList<>();
                citySequence.add(depot);
                citySequence.add(city);
                citySequence.add(depot);
                Map<String, Integer> deliveryMap = new HashMap<>();
                deliveryMap.put(city, delivered);
                Route route = new Route(citySequence, delivered, totalTime, totalCost, deliveryMap);
                routes.add(route);
                required -= delivered;
            }
        }
        return routes;
    }

    private Pair dijkstra(Graph graph, String start, String end) {
        PriorityQueue<Pair> pq = new PriorityQueue<>(Comparator.comparingInt(p -> p.time));
        Map<String, Integer> bestTime = new HashMap<>();

        for (String city : graph.getCities()) {
            bestTime.put(city, Integer.MAX_VALUE);
        }
        bestTime.put(start, 0);
        pq.add(new Pair(start, 0, 0.0));

        while (!pq.isEmpty()) {
            Pair current = pq.poll();
            if (current.city.equals(end)) {
                return current;
            }
            if (current.time > bestTime.get(current.city)) continue;
            for (Edge edge : graph.getNeighbors(current.city)) {
                int newTime = current.time + edge.getTime();
                double newCost = current.cost + edge.getCost();
                if (newTime < bestTime.get(edge.getDestination())) {
                    bestTime.put(edge.getDestination(), newTime);
                    pq.add(new Pair(edge.getDestination(), newTime, newCost));
                }
            }
        }
        
        throw new IllegalArgumentException("No feasible route");
    }
    
    private static class Pair {
        String city;
        int time;
        double cost;
        
        public Pair(String city, int time, double cost) {
            this.city = city;
            this.time = time;
            this.cost = cost;
        }
    }
}