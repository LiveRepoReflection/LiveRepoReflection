public class NetworkLatencyCalculator {

    public int minimumLatency(int n, int[][] partialConnectivity) {
        // Validate that all off-diagonal entries are either -1 or at least 1.
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    if (partialConnectivity[i][j] == 0) {
                        return -1;
                    }
                }
            }
        }

        // Build the complete connectivity matrix.
        // For each pair (i, j), if the latency is specified (not -1), use that value.
        // Otherwise, assign the minimum valid value, which is 1.
        int[][] dist = new int[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i == j) {
                    dist[i][j] = 0;
                } else {
                    if (partialConnectivity[i][j] != -1) {
                        dist[i][j] = partialConnectivity[i][j];
                    } else {
                        dist[i][j] = 1;
                    }
                }
            }
        }
        
        // Use Floyd Warshall algorithm to compute all-pairs shortest path distances.
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        
        // Compute the overall communication latency:
        // Sum of shortest paths for every unordered pair (i, j) with i < j.
        int totalLatency = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                totalLatency += dist[i][j];
            }
        }
        
        return totalLatency;
    }
}