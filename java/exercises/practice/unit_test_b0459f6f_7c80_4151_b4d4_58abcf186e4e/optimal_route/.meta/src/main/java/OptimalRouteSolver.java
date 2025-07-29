package optimal_route;

import java.util.*;
import java.lang.reflect.Field;

public class OptimalRouteSolver {

    private Map<String, List<Object>> graph;

    public OptimalRouteSolver(Map<String, ? extends List<?>> inputGraph) {
        // Convert the input graph to a uniform Map<String, List<Object>> for internal use.
        graph = new HashMap<>();
        for (Map.Entry<String, ? extends List<?>> entry : inputGraph.entrySet()) {
            List<Object> list = new ArrayList<>(entry.getValue());
            graph.put(entry.getKey(), list);
        }
    }

    public List<String> findOptimalRoute(String start, String destination, double maxTravelTime) {
        // Use a priority queue ordered by totalCost.
        PriorityQueue<State> pq = new PriorityQueue<>(Comparator.comparingDouble(s -> s.totalCost));
        // For pruning: for each node, maintain a list of non-dominated states.
        Map<String, List<State>> bestStates = new HashMap<>();

        State startState = new State(start, 0.0, 0.0, new ArrayList<>(Arrays.asList(start)));
        pq.add(startState);
        addState(bestStates, startState);

        while (!pq.isEmpty()) {
            State current = pq.poll();

            // If destination is reached under the maxTravelTime constraint, return the path.
            if (current.node.equals(destination)) {
                return current.path;
            }

            List<Object> edges = graph.getOrDefault(current.node, Collections.emptyList());
            for (Object edge : edges) {
                String neighbor = getStringField(edge, "target");
                double baseTravelTime = getDoubleField(edge, "baseTravelTime");
                double trafficFactor = getDoubleField(edge, "trafficFactor");
                double tollPrice = getDoubleField(edge, "tollPrice");

                double travelTimeForEdge = baseTravelTime * trafficFactor;
                double newTravelTime = current.totalTravelTime + travelTimeForEdge;

                if (newTravelTime > maxTravelTime) {
                    continue;
                }

                double newCost = current.totalCost + travelTimeForEdge + tollPrice;
                List<String> newPath = new ArrayList<>(current.path);
                newPath.add(neighbor);

                State newState = new State(neighbor, newTravelTime, newCost, newPath);

                if (isDominated(bestStates.get(neighbor), newState)) {
                    continue;
                }
                removeDominated(bestStates, neighbor, newState);
                addState(bestStates, newState);
                pq.add(newState);
            }
        }
        // Return null if no valid route is found within the constraints.
        return null;
    }

    // Reflection helper method to extract a double field value.
    private double getDoubleField(Object edge, String fieldName) {
        try {
            Field field = edge.getClass().getField(fieldName);
            return ((Number) field.get(edge)).doubleValue();
        } catch (Exception e) {
            throw new RuntimeException("Error accessing field " + fieldName, e);
        }
    }

    // Reflection helper method to extract a String field value.
    private String getStringField(Object edge, String fieldName) {
        try {
            Field field = edge.getClass().getField(fieldName);
            return (String) field.get(edge);
        } catch (Exception e) {
            throw new RuntimeException("Error accessing field " + fieldName, e);
        }
    }

    // Checks if newState is dominated by any of the states already recorded for a node.
    private boolean isDominated(List<State> states, State newState) {
        if (states == null) return false;
        for (State s : states) {
            if (s.totalTravelTime <= newState.totalTravelTime && s.totalCost <= newState.totalCost) {
                return true;
            }
        }
        return false;
    }

    // Removes any states that are dominated by newState.
    private void removeDominated(Map<String, List<State>> bestStates, String node, State newState) {
        List<State> states = bestStates.get(node);
        if (states == null) return;
        Iterator<State> iter = states.iterator();
        while (iter.hasNext()) {
            State s = iter.next();
            if (newState.totalTravelTime <= s.totalTravelTime && newState.totalCost <= s.totalCost) {
                iter.remove();
            }
        }
    }

    // Adds a new state for a node.
    private void addState(Map<String, List<State>> bestStates, State state) {
        bestStates.computeIfAbsent(state.node, k -> new ArrayList<>()).add(state);
    }

    // Inner class representing a state in the search.
    private static class State {
        String node;
        double totalTravelTime;
        double totalCost;
        List<String> path;

        State(String node, double totalTravelTime, double totalCost, List<String> path) {
            this.node = node;
            this.totalTravelTime = totalTravelTime;
            this.totalCost = totalCost;
            this.path = path;
        }
    }
}