public class MeetingPoint {

    public static int findMeetingPoint(int n, int[][] edges, int[] locations) {
        final int INF = Integer.MAX_VALUE / 2;
        int[][] dist = new int[n][n];
        
        // Initialize distance matrix
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i == j) {
                    dist[i][j] = 0;
                } else {
                    dist[i][j] = INF;
                }
            }
        }
        
        // Update distance matrix with edge weights (undirected graph)
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            if (w < dist[u][v]) {
                dist[u][v] = w;
                dist[v][u] = w;
            }
        }
        
        // Floyd-Warshall algorithm to compute all-pairs shortest paths
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                if (dist[i][k] == INF) continue;
                for (int j = 0; j < n; j++) {
                    if (dist[k][j] == INF) continue;
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        
        // Choose the meeting point that minimizes the maximum distance from any starting location
        int bestNode = -1;
        int bestMaxDistance = INF;
        for (int m = 0; m < n; m++) {
            int currentMax = 0;
            for (int loc : locations) {
                currentMax = Math.max(currentMax, dist[loc][m]);
            }
            if (currentMax < bestMaxDistance) {
                bestMaxDistance = currentMax;
                bestNode = m;
            }
        }
        
        // If no valid meeting point is found (all candidates unreachable), default to node 0.
        return bestNode == -1 ? 0 : bestNode;
    }
}