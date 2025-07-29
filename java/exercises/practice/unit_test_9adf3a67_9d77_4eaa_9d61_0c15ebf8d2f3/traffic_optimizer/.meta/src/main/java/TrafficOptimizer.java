import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class TrafficOptimizer {

    // A constant to represent infinity in our calculations.
    private static final double INF = 1e12;

    public List<int[]> optimizeTraffic(int numNodes,
                                         List<int[]> edges,
                                         List<Integer> criticalLocations,
                                         int numTrafficLights,
                                         double reductionPercentage) {
        // Create a working copy of edges. Each edge is represented by an int[] of {u, v, travelTime}.
        List<int[]> workingEdges = cloneEdges(edges);
        List<int[]> chosenPlacements = new ArrayList<>();
        // This set is used to ensure we do not install more than one traffic light on the same edge.
        Set<Integer> installedEdgeIndices = new HashSet<>();

        // Compute the baseline average travel time using the current workingEdges.
        double baselineAvg = computeAverageTravelTime(numNodes, workingEdges, criticalLocations);

        // Greedily select edges to install traffic lights
        for (int installed = 0; installed < numTrafficLights; installed++) {
            double bestImprovement = 0;
            int bestEdgeIndex = -1;
            double bestCandidateAvg = baselineAvg;
            // Try each edge that does not already have a traffic light.
            for (int i = 0; i < workingEdges.size(); i++) {
                if (installedEdgeIndices.contains(i)) {
                    continue;
                }
                // Simulate installing a traffic light on edge i.
                List<int[]> candidateEdges = cloneEdges(workingEdges);
                int[] candidateEdge = candidateEdges.get(i);
                // Apply reduction: new travel time becomes floor(currentTime * (1 - reductionPercentage))
                candidateEdge[2] = (int) Math.floor(candidateEdge[2] * (1 - reductionPercentage));
                // Compute the average travel time with this candidate change.
                double candidateAvg = computeAverageTravelTime(numNodes, candidateEdges, criticalLocations);
                double improvement = baselineAvg - candidateAvg;
                if (improvement > bestImprovement) {
                    bestImprovement = improvement;
                    bestEdgeIndex = i;
                    bestCandidateAvg = candidateAvg;
                }
            }
            // If no improvement found, break out.
            if (bestEdgeIndex == -1) {
                break;
            }
            // Permanently apply the best found reduction.
            int[] bestEdge = workingEdges.get(bestEdgeIndex);
            bestEdge[2] = (int) Math.floor(bestEdge[2] * (1 - reductionPercentage));
            installedEdgeIndices.add(bestEdgeIndex);
            chosenPlacements.add(new int[]{bestEdge[0], bestEdge[1]});
            baselineAvg = bestCandidateAvg;
        }
        return chosenPlacements;
    }

    /**
     * Helper method to clone the list of edges.
     */
    private List<int[]> cloneEdges(List<int[]> edges) {
        List<int[]> cloned = new ArrayList<>();
        for (int[] edge : edges) {
            cloned.add(Arrays.copyOf(edge, edge.length));
        }
        return cloned;
    }

    /**
     * Computes the average shortest path travel time between all ordered pairs of critical locations.
     * If a pair is not reachable, its travel time is considered INF.
     */
    private double computeAverageTravelTime(int numNodes,
                                            List<int[]> edges,
                                            List<Integer> criticalLocations) {
        double[][] dist = new double[numNodes][numNodes];
        // Initialize distances.
        for (int i = 0; i < numNodes; i++) {
            Arrays.fill(dist[i], INF);
            dist[i][i] = 0;
        }
        // For each edge, update the distance matrix.
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            double weight = edge[2];
            dist[u][v] = Math.min(dist[u][v], weight);
        }
        // Floyd-Warshall algorithm for all pairs shortest paths.
        for (int k = 0; k < numNodes; k++) {
            for (int i = 0; i < numNodes; i++) {
                for (int j = 0; j < numNodes; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        // Compute average over all ordered pairs (u, v) for critical locations (u != v)
        double sum = 0;
        int count = 0;
        for (int i = 0; i < criticalLocations.size(); i++) {
            for (int j = 0; j < criticalLocations.size(); j++) {
                if (i == j) {
                    continue;
                }
                int u = criticalLocations.get(i);
                int v = criticalLocations.get(j);
                sum += dist[u][v];
                count++;
            }
        }
        return (count == 0) ? INF : sum / count;
    }
}