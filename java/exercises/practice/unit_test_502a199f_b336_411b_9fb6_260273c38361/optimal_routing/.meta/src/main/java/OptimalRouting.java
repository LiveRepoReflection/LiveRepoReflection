import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

public class OptimalRouting {

    // Internal class to represent an edge in the graph.
    static class Edge {
        int to;
        int travelTime;
        int tollCost;
        Edge(int to, int travelTime, int tollCost) {
            this.to = to;
            this.travelTime = travelTime;
            this.tollCost = tollCost;
        }
    }
    
    // Pair to store both travel time and toll cost.
    static class Pair {
        int time;
        int toll;
        Pair(int time, int toll) {
            this.time = time;
            this.toll = toll;
        }
    }
    
    // State used in DP for route planning among candidates.
    static class State {
        int arrivalTime;
        double cost;
        State(int arrivalTime, double cost) {
            this.arrivalTime = arrivalTime;
            this.cost = cost;
        }
    }
    
    // Node state for multi-criteria Dijkstra.
    static class NodeState {
        int node;
        int time;
        int toll;
        NodeState(int node, int time, int toll) {
            this.node = node;
            this.time = time;
            this.toll = toll;
        }
    }
    
    // Check if pair a dominates pair b.
    private static boolean dominates(Pair a, Pair b) {
        return (a.time <= b.time && a.toll <= b.toll) && (a.time < b.time || a.toll < b.toll);
    }
    
    // Add a new pair to the Pareto front list if it is not dominated.
    private static boolean addPair(List<Pair> list, Pair newPair) {
        List<Pair> toRemove = new ArrayList<>();
        for (Pair p : list) {
            if (dominates(p, newPair)) {
                return false; // newPair is dominated.
            }
            if (dominates(newPair, p)) {
                toRemove.add(p);
            }
        }
        list.removeAll(toRemove);
        list.add(newPair);
        return true;
    }
    
    // Modified multi-criteria Dijkstra to compute Pareto optimal (time, toll) pairs from source 's' to all nodes.
    private static List<List<Pair>> multiCriteriaDijkstra(int s, List<List<Edge>> graph, int numLocations) {
        List<List<Pair>> best = new ArrayList<>(numLocations);
        for (int i = 0; i < numLocations; i++) {
            best.add(new ArrayList<>());
        }
        // Initialize source.
        best.get(s).add(new Pair(0, 0));
        
        // PriorityQueue ordered by travel time first then toll cost.
        PriorityQueue<NodeState> pq = new PriorityQueue<>((a, b) -> {
            if (a.time != b.time) {
                return Integer.compare(a.time, b.time);
            }
            return Integer.compare(a.toll, b.toll);
        });
        pq.offer(new NodeState(s, 0, 0));
        
        while (!pq.isEmpty()) {
            NodeState curr = pq.poll();
            // Check if current state is still Pareto optimal.
            boolean valid = false;
            for (Pair p : best.get(curr.node)) {
                if (p.time == curr.time && p.toll == curr.toll) {
                    valid = true;
                    break;
                }
            }
            if (!valid) continue;
            
            // Explore neighbors.
            for (Edge edge : graph.get(curr.node)) {
                int newTime = curr.time + edge.travelTime;
                int newToll = curr.toll + edge.tollCost;
                Pair newPair = new Pair(newTime, newToll);
                if (addPair(best.get(edge.to), newPair)) {
                    pq.offer(new NodeState(edge.to, newTime, newToll));
                }
            }
        }
        return best;
    }
    
    // The main function that computes the minimal cost route covering all delivery destinations.
    public static double findOptimalRouteCost(
            int numLocations, 
            List<int[]> roads, 
            List<Integer> deliveryDestinations, 
            Map<Integer, int[]> deliveryWindows, 
            double timeWeight, 
            double tollWeight) {
        
        // Build the graph.
        List<List<Edge>> graph = new ArrayList<>(numLocations);
        for (int i = 0; i < numLocations; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] road : roads) {
            int from = road[0];
            int to = road[1];
            int travelTime = road[2];
            int tollCost = road[3];
            graph.get(from).add(new Edge(to, travelTime, tollCost));
        }
        
        // Build candidate list: candidateIndices[0] is depot (node 0), remaining are deliveryDestinations.
        List<Integer> candidateNodes = new ArrayList<>();
        candidateNodes.add(0); // depot
        // Use a set to avoid duplicate deliveries if any.
        Set<Integer> uniqueDeliveries = new HashSet<>(deliveryDestinations);
        for (Integer d : uniqueDeliveries) {
            candidateNodes.add(d);
        }
        int candidateCount = candidateNodes.size();
        int K = candidateCount - 1; // number of deliveries
        
        // Precompute Pareto optimal pairs for each candidate source to every candidate destination.
        // connections[i][j] will be a list of Pareto optimal pairs (travelTime, toll) from candidate i to candidate j.
        List<List<List<Pair>>> connections = new ArrayList<>();
        for (int i = 0; i < candidateCount; i++) {
            // Run multi-criteria Dijkstra from candidateNodes.get(i)
            int sourceNode = candidateNodes.get(i);
            List<List<Pair>> bestFromSource = multiCriteriaDijkstra(sourceNode, graph, numLocations);
            List<List<Pair>> connectionFromI = new ArrayList<>();
            for (int j = 0; j < candidateCount; j++) {
                int targetNode = candidateNodes.get(j);
                // Copy Pareto front for target node.
                List<Pair> pairs = new ArrayList<>(bestFromSource.get(targetNode));
                connectionFromI.add(pairs);
            }
            connections.add(connectionFromI);
        }
        
        // DP over subsets of delivery destinations.
        // dp[mask][i] stores Pareto optimal states (arrivalTime, cost) with visited deliveries given by mask and current candidate index i.
        int totalMasks = 1 << K;
        List<List<List<State>>> dp = new ArrayList<>(totalMasks);
        for (int mask = 0; mask < totalMasks; mask++) {
            List<List<State>> statesForMask = new ArrayList<>();
            for (int i = 0; i < candidateCount; i++) {
                statesForMask.add(new ArrayList<>());
            }
            dp.add(statesForMask);
        }
        // Start at depot at time 0 and cost 0.
        dp.get(0).get(0).add(new State(0, 0.0));
        
        // For each DP state
        for (int mask = 0; mask < totalMasks; mask++) {
            for (int i = 0; i < candidateCount; i++) {
                List<State> stateList = dp.get(mask).get(i);
                if (stateList.isEmpty()) continue;
                for (int j = 1; j < candidateCount; j++) { // j from 1 to candidateCount-1 represent deliveries
                    // If j is already visited in mask, skip.
                    if ((mask & (1 << (j - 1))) != 0) continue;
                    int[] window = deliveryWindows.get(candidateNodes.get(j));
                    if (window == null) continue; // No window provided, skip this candidate.
                    int windowStart = window[0];
                    int windowEnd = window[1];
                    List<Pair> routeOptions = connections.get(i).get(j);
                    if (routeOptions.isEmpty()) continue; // unreachable.
                    int newMask = mask | (1 << (j - 1));
                    List<State> nextStates = dp.get(newMask).get(j);
                    for (State st : stateList) {
                        for (Pair pr : routeOptions) {
                            int arrivalCandidate = st.arrivalTime + pr.time;
                            int effectiveArrival = Math.max(arrivalCandidate, windowStart);
                            if (effectiveArrival > windowEnd) {
                                continue; // cannot meet window.
                            }
                            double newCost = st.cost + timeWeight * pr.time + tollWeight * pr.toll;
                            State newState = new State(effectiveArrival, newCost);
                            // Add newState to nextStates if not dominated.
                            boolean dominated = false;
                            List<State> toRemove = new ArrayList<>();
                            for (State exist : nextStates) {
                                if (exist.arrivalTime <= newState.arrivalTime && exist.cost <= newState.cost) {
                                    dominated = true;
                                    break;
                                }
                                if (newState.arrivalTime <= exist.arrivalTime && newState.cost <= exist.cost) {
                                    toRemove.add(exist);
                                }
                            }
                            if (!dominated) {
                                nextStates.removeAll(toRemove);
                                nextStates.add(newState);
                            }
                        }
                    }
                }
            }
        }
        
        // Find the minimal cost across all states that have visited all deliveries.
        double answer = Double.MAX_VALUE;
        for (int i = 1; i < candidateCount; i++) {
            for (State st : dp.get(totalMasks - 1).get(i)) {
                answer = Math.min(answer, st.cost);
            }
        }
        
        return answer;
    }
}