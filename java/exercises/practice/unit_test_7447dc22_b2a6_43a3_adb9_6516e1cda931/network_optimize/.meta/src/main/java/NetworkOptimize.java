import java.util.*;

public class NetworkOptimize {
    private static final int INF = 100000000;

    public int[][] optimizeDistribution(int n, int[][] matrix, int[] serverCapacities, int[] fileSizes, int k, int[][] requests) {
        int numFiles = fileSizes.length;
        // Compute all pairs shortest paths using Floyd Warshall
        int[][] dist = new int[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(dist[i], INF);
            for (int j = 0; j < n; j++) {
                if(i == j) {
                    dist[i][j] = 0;
                } else if(matrix[i][j] != -1) {
                    dist[i][j] = matrix[i][j];
                }
            }
        }
        for (int k1 = 0; k1 < n; k1++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if(dist[i][k1] + dist[k1][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k1] + dist[k1][j];
                    }
                }
            }
        }
        
        // Precompute request frequency per file per server.
        int[][] freq = new int[numFiles][n];
        for (int[] req : requests) {
            int requester = req[0];
            int fileId = req[1];
            if (fileId >= 0 && fileId < numFiles && requester >= 0 && requester < n) {
                freq[fileId][requester]++;
            }
        }
        
        // Compute total requests per file
        Integer[] filesOrder = new Integer[numFiles];
        for (int f = 0; f < numFiles; f++) {
            filesOrder[f] = f;
        }
        Arrays.sort(filesOrder, (a, b) -> {
            int totalA = 0, totalB = 0;
            for (int i = 0; i < n; i++) {
                totalA += freq[a][i];
                totalB += freq[b][i];
            }
            return Integer.compare(totalB, totalA);
        });
        
        // Result distribution matrix and used capacity tracker for servers.
        int[][] distribution = new int[n][numFiles];
        int[] usedCapacity = new int[n];
        
        // Process each file in order of decreasing demand.
        for (int idx = 0; idx < numFiles; idx++) {
            int fileId = filesOrder[idx];
            int fileSize = fileSizes[fileId];
            // For this file, we need to select k servers.
            List<Integer> selected = new ArrayList<>();
            // currentCost per requester server: best distance from requester to any chosen replication server for this file.
            int[] currentCost = new int[n];
            Arrays.fill(currentCost, INF);
            
            // Greedy facility location approach to choose k replication servers.
            for (int rep = 0; rep < k; rep++) {
                double bestImprovement = -1;
                int bestCandidate = -1;
                double bestCandidateCostSum = INF; // used if improvements are equal
                // Iterate over candidate servers.
                for (int i = 0; i < n; i++) {
                    // Already selected?
                    if (selected.contains(i)) continue;
                    // Check capacity constraint
                    if (serverCapacities[i] - usedCapacity[i] < fileSize) continue;
                    
                    double improvement = 0;
                    double costSum = 0;
                    for (int s = 0; s < n; s++) {
                        int newCost = Math.min(currentCost[s], dist[s][i]);
                        improvement += ((long) freq[fileId][s]) * (currentCost[s] - newCost);
                        costSum += ((long) freq[fileId][s]) * dist[s][i];
                    }
                    // Choose candidate with positive improvement first.
                    if (improvement > bestImprovement) {
                        bestImprovement = improvement;
                        bestCandidate = i;
                        bestCandidateCostSum = costSum;
                    } else if (improvement == bestImprovement && improvement == 0) {
                        // Tiebreaker: choose candidate with lower cost sum.
                        if (costSum < bestCandidateCostSum) {
                            bestCandidate = i;
                            bestCandidateCostSum = costSum;
                        }
                    }
                }
                if (bestCandidate == -1) {
                    return null; // no candidate found that satisfies capacity constraints.
                }
                // Update currentCost for all requester servers.
                for (int s = 0; s < n; s++) {
                    currentCost[s] = Math.min(currentCost[s], dist[s][bestCandidate]);
                }
                selected.add(bestCandidate);
                usedCapacity[bestCandidate] += fileSize;
                distribution[bestCandidate][fileId] = 1;
            }
            // After k assignments, verify that for every requester that made at least one request for this file,
            // there is at least one reachable replication server.
            for (int s = 0; s < n; s++) {
                if (freq[fileId][s] > 0 && currentCost[s] >= INF) {
                    return null; // Some request cannot reach any replication server for this file.
                }
            }
        }
        return distribution;
    }
}