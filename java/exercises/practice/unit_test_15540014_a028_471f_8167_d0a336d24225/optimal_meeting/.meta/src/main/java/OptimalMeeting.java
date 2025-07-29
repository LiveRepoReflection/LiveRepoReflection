package optimal_meeting;

import java.util.Arrays;

public class OptimalMeeting {

    /**
     * Finds the optimal meeting point that minimizes the total travel time for all engineers.
     *
     * @param n                 the number of nodes (locations)
     * @param roads             the list of roads, where each road is represented as [location1, location2, travel_time]
     * @param engineerLocations the list of locations of the engineers
     * @return the optimal meeting location index
     */
    public static int findOptimalMeetingPoint(int n, int[][] roads, int[] engineerLocations) {
        // Initialize the distance matrix using Floyd-Warshall algorithm
        long INF = Long.MAX_VALUE / 2;
        long[][] dist = new long[n][n];
        for (int i = 0; i < n; i++) {
            Arrays.fill(dist[i], INF);
            dist[i][i] = 0;
        }
        
        // Fill the direct distances based on given roads (undirected)
        for (int[] road : roads) {
            int u = road[0];
            int v = road[1];
            int w = road[2];
            if (w < 0) continue; // safeguard; no negative weights expected
            dist[u][v] = Math.min(dist[u][v], w);
            dist[v][u] = Math.min(dist[v][u], w);
        }
        
        // Run Floyd-Warshall to compute shortest paths between all pairs
        for (int k = 0; k < n; k++) {
            for (int i = 0; i < n; i++) {
                if (dist[i][k] == INF) continue;
                for (int j = 0; j < n; j++) {
                    if (dist[i][k] + dist[k][j] < dist[i][j]) {
                        dist[i][j] = dist[i][k] + dist[k][j];
                    }
                }
            }
        }
        
        // Determine the optimal meeting point by checking each location
        int optimalLocation = -1;
        long minimalTotal = INF;
        for (int loc = 0; loc < n; loc++) {
            long totalTime = 0;
            boolean reachable = true;
            for (int engineer : engineerLocations) {
                if (dist[engineer][loc] == INF) {
                    reachable = false;
                    break;
                }
                totalTime += dist[engineer][loc];
            }
            if (reachable && totalTime < minimalTotal) {
                minimalTotal = totalTime;
                optimalLocation = loc;
            }
        }
        
        return optimalLocation;
    }
}