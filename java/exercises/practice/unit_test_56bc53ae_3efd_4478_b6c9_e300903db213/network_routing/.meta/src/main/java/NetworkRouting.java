import java.util.*;

public class NetworkRouting {
    
    private static class Edge {
        int to;
        int latency;
        int bandwidth;
        
        Edge(int to, int latency, int bandwidth) {
            this.to = to;
            this.latency = latency;
            this.bandwidth = bandwidth;
        }
    }
    
    private static class Path implements Comparable<Path> {
        int node;
        int minBandwidth;
        int totalLatency;
        int hops;
        
        Path(int node, int minBandwidth, int totalLatency, int hops) {
            this.node = node;
            this.minBandwidth = minBandwidth;
            this.totalLatency = totalLatency;
            this.hops = hops;
        }
        
        @Override
        public int compareTo(Path other) {
            // First compare by bandwidth (higher is better)
            if (this.minBandwidth != other.minBandwidth) {
                return Integer.compare(other.minBandwidth, this.minBandwidth);
            }
            // Then by number of hops (fewer is better)
            if (this.hops != other.hops) {
                return Integer.compare(this.hops, other.hops);
            }
            // Finally by latency (lower is better)
            return Integer.compare(this.totalLatency, other.totalLatency);
        }
    }
    
    /**
     * Finds the optimal path from source to destination with maximum bandwidth
     * while satisfying latency constraints.
     *
     * @param n     Number of nodes in the network
     * @param edges List of edges, each represented as [u, v, latency, bandwidth]
     * @param s     Source node
     * @param d     Destination node
     * @param b     Minimum required bandwidth
     * @param l     Maximum acceptable latency
     * @return Maximum achievable bandwidth, or -1 if no valid path exists
     */
    public int findOptimalPath(int n, List<int[]> edges, int s, int d, int b, int l) {
        // Handle special case: source and destination are the same
        if (s == d) {
            return b; // Return minimum required bandwidth as there's no actual path
        }
        
        // Build adjacency list
        List<List<Edge>> graph = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int latency = edge[2];
            int bandwidth = edge[3];
            
            // Skip edges that don't meet minimum bandwidth requirement
            if (bandwidth < b) {
                continue;
            }
            
            // Add bidirectional edges
            graph.get(u).add(new Edge(v, latency, bandwidth));
            graph.get(v).add(new Edge(u, latency, bandwidth));
        }
        
        // Dijkstra's algorithm with modified priority
        PriorityQueue<Path> pq = new PriorityQueue<>();
        pq.offer(new Path(s, Integer.MAX_VALUE, 0, 0));
        
        // Keep track of best path to each node
        // For each node, store [minBandwidth, totalLatency, hops]
        Map<Integer, int[]> bestPaths = new HashMap<>();
        
        while (!pq.isEmpty()) {
            Path current = pq.poll();
            int node = current.node;
            int minBandwidth = current.minBandwidth;
            int totalLatency = current.totalLatency;
            int hops = current.hops;
            
            // If we've reached the destination, return the result
            if (node == d) {
                return minBandwidth;
            }
            
            // Skip if we've already found a better path to this node
            if (bestPaths.containsKey(node)) {
                int[] best = bestPaths.get(node);
                if (best[0] > minBandwidth || 
                    (best[0] == minBandwidth && best[1] <= totalLatency && best[2] <= hops)) {
                    continue;
                }
            }
            
            // Update best path to this node
            bestPaths.put(node, new int[]{minBandwidth, totalLatency, hops});
            
            // Explore neighbors
            for (Edge edge : graph.get(node)) {
                int newLatency = totalLatency + edge.latency;
                
                // Skip if latency exceeds limit
                if (newLatency > l) {
                    continue;
                }
                
                int newBandwidth = Math.min(minBandwidth, edge.bandwidth);
                pq.offer(new Path(edge.to, newBandwidth, newLatency, hops + 1));
            }
        }
        
        // No valid path found
        return -1;
    }
    
    // Binary search approach with optimization
    public int findOptimalPathBinarySearch(int n, List<int[]> edges, int s, int d, int b, int l) {
        // Special case: source and destination are the same
        if (s == d) {
            return b;
        }
        
        // Sort edges by bandwidth in descending order
        List<int[]> sortedEdges = new ArrayList<>(edges);
        sortedEdges.sort((e1, e2) -> Integer.compare(e2[3], e1[3]));
        
        // Find the maximum potential bandwidth
        int maxBandwidth = 0;
        for (int[] edge : edges) {
            maxBandwidth = Math.max(maxBandwidth, edge[3]);
        }
        
        if (maxBandwidth < b) {
            return -1; // No edge can satisfy the minimum bandwidth
        }
        
        // Binary search for the optimal bandwidth
        int left = b;
        int right = maxBandwidth;
        int result = -1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (pathExists(n, sortedEdges, s, d, mid, l)) {
                result = mid;
                left = mid + 1; // Try to find a better bandwidth
            } else {
                right = mid - 1; // Try a lower bandwidth
            }
        }
        
        return result;
    }
    
    // Check if there's a path from s to d with at least bandwidth b and at most latency l
    private boolean pathExists(int n, List<int[]> edges, int s, int d, int bandwidth, int l) {
        // Build graph with only edges that meet the bandwidth requirement
        List<List<int[]>> graph = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] edge : edges) {
            if (edge[3] >= bandwidth) { // Only consider edges with sufficient bandwidth
                int u = edge[0];
                int v = edge[1];
                int latency = edge[2];
                
                graph.get(u).add(new int[]{v, latency});
                graph.get(v).add(new int[]{u, latency});
            }
        }
        
        // Dijkstra's algorithm to find the shortest path by latency
        int[] dist = new int[n];
        int[] hops = new int[n];
        Arrays.fill(dist, Integer.MAX_VALUE);
        Arrays.fill(hops, Integer.MAX_VALUE);
        dist[s] = 0;
        hops[s] = 0;
        
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> {
            // Compare first by latency
            if (a[1] != b[1]) return Integer.compare(a[1], b[1]);
            // Then by hops
            return Integer.compare(a[2], b[2]);
        });
        pq.offer(new int[]{s, 0, 0}); // node, latency, hops
        
        boolean[] visited = new boolean[n];
        
        while (!pq.isEmpty()) {
            int[] curr = pq.poll();
            int node = curr[0];
            int latency = curr[1];
            int hop = curr[2];
            
            if (visited[node]) continue;
            visited[node] = true;
            
            if (node == d) {
                return true; // Path found
            }
            
            for (int[] neighbor : graph.get(node)) {
                int nextNode = neighbor[0];
                int nextLatency = latency + neighbor[1];
                
                if (nextLatency <= l && !visited[nextNode]) {
                    if (nextLatency < dist[nextNode] || 
                        (nextLatency == dist[nextNode] && hop + 1 < hops[nextNode])) {
                        dist[nextNode] = nextLatency;
                        hops[nextNode] = hop + 1;
                        pq.offer(new int[]{nextNode, nextLatency, hop + 1});
                    }
                }
            }
        }
        
        return false; // No path found
    }
}