package route_optim;

import java.util.*;

public class RouteOptim {

    // Edge class representing a directed edge in the graph.
    public static class Edge {
        public int destination;
        public int travelTime;
        public int congestionScore;
        
        public Edge(int destination, int travelTime, int congestionScore) {
            this.destination = destination;
            this.travelTime = travelTime;
            this.congestionScore = congestionScore;
        }
    }

    // DeliveryRequest representing a single delivery request.
    public static class DeliveryRequest {
        public int start;
        public int end;
        public int priority;
        
        public DeliveryRequest(int start, int end, int priority) {
            this.start = start;
            this.end = end;
            this.priority = priority;
        }
    }
    
    // State class used in the Dijkstra-like search.
    private static class State {
        int node;
        int totalTime;
        int totalCongestion;
        double cost;
        State parent;
        
        State(int node, int totalTime, int totalCongestion, double cost, State parent) {
            this.node = node;
            this.totalTime = totalTime;
            this.totalCongestion = totalCongestion;
            this.cost = cost;
            this.parent = parent;
        }
    }
    
    /**
     * Finds the optimal routes for each delivery request.
     *
     * @param graph the city graph represented as an adjacency list.
     * @param requests list of delivery requests.
     * @param drivers number of drivers available (not used in current routing, can be extended).
     * @param T maximum route duration allowed.
     * @param C congestion threshold allowed.
     * @param alpha weight parameter between travel time and congestion.
     * @return a list of routes, each route is a list of node IDs.
     */
    public List<List<Integer>> findOptimalRoutes(Map<Integer, List<Edge>> graph, List<DeliveryRequest> requests, int drivers, int T, int C, double alpha) {
        List<List<Integer>> result = new ArrayList<>();
        for (DeliveryRequest request : requests) {
            List<Integer> path = findRoute(graph, request.start, request.end, T, C, alpha);
            result.add(path);
        }
        return result;
    }
    
    // Uses a modified Dijkstra's algorithm to compute route that minimizes (alpha * time + (1-alpha) * congestion)
    // while satisfying constraints.
    private List<Integer> findRoute(Map<Integer, List<Edge>> graph, int start, int end, int maxTime, int maxCongestion, double alpha) {
        if (start == end) {
            return Arrays.asList(start);
        }
        
        // Priority queue ordered by cost
        PriorityQueue<State> pq = new PriorityQueue<>(Comparator.comparingDouble(s -> s.cost));
        State startState = new State(start, 0, 0, 0.0, null);
        pq.offer(startState);
        
        // For each node, maintain a list of non-dominated pairs (time, congestion)
        Map<Integer, List<State>> bestStates = new HashMap<>();
        bestStates.put(start, new ArrayList<>(Arrays.asList(startState)));
        
        while(!pq.isEmpty()){
            State current = pq.poll();
            if(current.node == end){
                return reconstructPath(current);
            }
            
            // Get neighbors
            List<Edge> edges = graph.getOrDefault(current.node, new ArrayList<>());
            for(Edge edge : edges) {
                int newTime = current.totalTime + edge.travelTime;
                int newCongestion = current.totalCongestion + edge.congestionScore;
                if(newTime > maxTime || newCongestion > maxCongestion) {
                    continue;
                }
                double newCost = alpha * newTime + (1 - alpha) * newCongestion;
                State nextState = new State(edge.destination, newTime, newCongestion, newCost, current);
                
                if(isDominated(bestStates.getOrDefault(edge.destination, new ArrayList<>()), newTime, newCongestion)) {
                    continue;
                }
                // Remove now dominated states from bestStates list
                List<State> list = bestStates.getOrDefault(edge.destination, new ArrayList<>());
                Iterator<State> iter = list.iterator();
                while(iter.hasNext()){
                    State s = iter.next();
                    if(s.totalTime >= newTime && s.totalCongestion >= newCongestion) {
                        iter.remove();
                    }
                }
                list.add(nextState);
                bestStates.put(edge.destination, list);
                pq.offer(nextState);
            }
        }
        
        // Return empty route if no valid route is found.
        return new ArrayList<>();
    }
    
    // Checks if there is any state in list that dominates the new state.
    private boolean isDominated(List<State> states, int time, int congestion) {
        for(State s : states) {
            if(s.totalTime <= time && s.totalCongestion <= congestion) {
                return true;
            }
        }
        return false;
    }

    // Reconstruct path from destination state to start by following parent pointers.
    private List<Integer> reconstructPath(State state) {
        List<Integer> path = new ArrayList<>();
        while(state != null) {
            path.add(state.node);
            state = state.parent;
        }
        Collections.reverse(path);
        return path;
    }
}