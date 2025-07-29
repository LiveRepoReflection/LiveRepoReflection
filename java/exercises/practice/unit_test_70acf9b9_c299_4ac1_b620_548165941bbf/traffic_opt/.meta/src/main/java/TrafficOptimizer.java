import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.PriorityQueue;
import java.util.ArrayList;

public class TrafficOptimizer {

    public OptimizationResult optimize(List<Integer> intersections, List<Road> roads, List<OdPair> odPairs, int minCycleTime, int maxCycleTime, int minGreenTime) {
        // For simplicity, choose the cycle time as the minimum cycle time.
        int cycleTime = minCycleTime;

        // Assume each intersection has 2 phases with pre-defined groups.
        // We assign each phase at least minGreenTime, and distribute any extra time equally.
        int numberOfPhases = 2;
        Map<Integer, Map<Integer, Integer>> schedule = new HashMap<>();
        for (Integer intersection : intersections) {
            Map<Integer, Integer> phaseGreenTimes = new HashMap<>();
            int totalMinGreen = numberOfPhases * minGreenTime;
            int extraTime = cycleTime - totalMinGreen;
            int extraPerPhase = (extraTime > 0) ? extraTime / numberOfPhases : 0;
            // Assign green time for phase 1 and phase 2
            phaseGreenTimes.put(1, minGreenTime + extraPerPhase);
            phaseGreenTimes.put(2, minGreenTime + extraPerPhase);
            // Adjust if there is any leftover
            int remaining = cycleTime - (phaseGreenTimes.get(1) + phaseGreenTimes.get(2));
            if (remaining > 0) {
                phaseGreenTimes.put(1, phaseGreenTimes.get(1) + remaining);
            }
            schedule.put(intersection, phaseGreenTimes);
        }

        // Build graph representation for path finding: Map<source, List<Road>>
        Map<Integer, List<Road>> graph = new HashMap<>();
        for (Integer intersection : intersections) {
            graph.put(intersection, new ArrayList<>());
        }
        for (Road road : roads) {
            if (graph.containsKey(road.getSource())) {
                graph.get(road.getSource()).add(road);
            }
        }

        // Compute average travel time over all OD pairs
        double totalWeightedTravelTime = 0.0;
        int totalDemand = 0;
        for (OdPair od : odPairs) {
            // If no demand, skip calculation for this OD pair.
            if (od.getDemand() == 0) {
                continue;
            }
            double travelTime = dijkstra(od.getOrigin(), od.getDestination(), graph, cycleTime);
            if (travelTime == Double.MAX_VALUE) {
                // If an OD pair is unreachable, return error.
                return new OptimizationResult(cycleTime, schedule, Double.MAX_VALUE, "Unreachable destination for OD pair: " + od.getOrigin() + "->" + od.getDestination());
            }
            totalWeightedTravelTime += travelTime * od.getDemand();
            totalDemand += od.getDemand();
        }
        double averageTravelTime = 0.0;
        if (totalDemand != 0) {
            averageTravelTime = totalWeightedTravelTime / totalDemand;
        }

        return new OptimizationResult(cycleTime, schedule, averageTravelTime, "");
    }

    // Custom implementation of Dijkstra algorithm.
    private double dijkstra(int start, int end, Map<Integer, List<Road>> graph, int cycleTime) {
        // waiting delay at each intersection (simulate traffic light delay) - assume waiting time equals half of the cycle time.
        double waitingDelay = cycleTime / 2.0;

        Map<Integer, Double> dist = new HashMap<>();
        for (Integer node : graph.keySet()) {
            dist.put(node, Double.MAX_VALUE);
        }
        dist.put(start, 0.0);

        // Priority queue based on current travel time
        PriorityQueue<NodeState> pq = new PriorityQueue<>((a, b) -> Double.compare(a.cost, b.cost));
        pq.offer(new NodeState(start, 0.0));

        while (!pq.isEmpty()) {
            NodeState current = pq.poll();
            if (current.node == end) {
                return current.cost;
            }
            if (current.cost > dist.get(current.node)) {
                continue;
            }
            List<Road> neighbors = graph.get(current.node);
            if (neighbors == null) {
                continue;
            }
            for (Road road : neighbors) {
                int neighbor = road.getDestination();
                double timeToNeighbor = road.getTravelTime();
                // Add waiting delay if neighbor is not the destination.
                if (neighbor != end) {
                    timeToNeighbor += waitingDelay;
                }
                double newCost = current.cost + timeToNeighbor;
                if (newCost < dist.get(neighbor)) {
                    dist.put(neighbor, newCost);
                    pq.offer(new NodeState(neighbor, newCost));
                }
            }
        }
        return Double.MAX_VALUE;
    }

    // Helper class for Dijkstra algorithm.
    private static class NodeState {
        int node;
        double cost;

        public NodeState(int node, double cost) {
            this.node = node;
            this.cost = cost;
        }
    }
}