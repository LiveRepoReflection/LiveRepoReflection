import java.util.*;

/**
 * NetworkRouting - A sophisticated routing system for a large-scale data center network.
 * This implementation handles dynamic network topology changes and provides efficient
 * optimal path finding between any two servers in the network.
 */
public class NetworkRouting {
    // Graph representation: adjacency list with latency values
    private final Map<Integer, Map<Integer, Integer>> graph;
    private final int numServers;
    
    // For congestion awareness (bonus feature)
    private final Map<Integer, Map<Integer, Integer>> trafficVolume;
    
    /**
     * RoutingResult class to encapsulate path and latency information.
     */
    public static class RoutingResult {
        private final int[] path;
        private final double totalLatency;
        
        public RoutingResult(int[] path, double totalLatency) {
            this.path = path;
            this.totalLatency = totalLatency;
        }
        
        public int[] getPath() {
            return path;
        }
        
        public double getTotalLatency() {
            return totalLatency;
        }
    }
    
    /**
     * Initialize the routing system with a given number of servers and initial links.
     * 
     * @param n Number of servers in the network
     * @param initialLinks List of initial links, each represented as [server1, server2, latency]
     */
    public NetworkRouting(int n, List<int[]> initialLinks) {
        this.numServers = n;
        this.graph = new HashMap<>();
        this.trafficVolume = new HashMap<>();
        
        // Initialize the graph
        for (int i = 0; i < n; i++) {
            graph.put(i, new HashMap<>());
            trafficVolume.put(i, new HashMap<>());
        }
        
        // Add initial links
        for (int[] link : initialLinks) {
            addLink(link[0], link[1], link[2]);
        }
    }
    
    /**
     * Add a new bidirectional link between two servers.
     * 
     * @param server1 First server ID
     * @param server2 Second server ID
     * @param latency Link latency
     */
    public void addLink(int server1, int server2, int latency) {
        // Ensure both servers exist in the graph
        if (server1 >= numServers || server2 >= numServers || server1 < 0 || server2 < 0) {
            throw new IllegalArgumentException("Server ID out of range");
        }
        
        // Add bidirectional link
        graph.get(server1).put(server2, latency);
        graph.get(server2).put(server1, latency);
        
        // Initialize traffic volume for this link
        trafficVolume.get(server1).put(server2, 0);
        trafficVolume.get(server2).put(server1, 0);
    }
    
    /**
     * Remove a bidirectional link between two servers.
     * 
     * @param server1 First server ID
     * @param server2 Second server ID
     */
    public void removeLink(int server1, int server2) {
        // Remove bidirectional link if it exists
        if (graph.containsKey(server1)) {
            graph.get(server1).remove(server2);
        }
        if (graph.containsKey(server2)) {
            graph.get(server2).remove(server1);
        }
        
        // Remove traffic data
        if (trafficVolume.containsKey(server1)) {
            trafficVolume.get(server1).remove(server2);
        }
        if (trafficVolume.containsKey(server2)) {
            trafficVolume.get(server2).remove(server1);
        }
    }
    
    /**
     * Update the latency of an existing bidirectional link between two servers.
     * 
     * @param server1 First server ID
     * @param server2 Second server ID
     * @param newLatency New link latency
     */
    public void updateLatency(int server1, int server2, int newLatency) {
        // Ensure the link exists before updating
        if (graph.containsKey(server1) && graph.get(server1).containsKey(server2) &&
            graph.containsKey(server2) && graph.get(server2).containsKey(server1)) {
            
            graph.get(server1).put(server2, newLatency);
            graph.get(server2).put(server1, newLatency);
        } else {
            throw new IllegalArgumentException("Link does not exist");
        }
    }
    
    /**
     * Find the optimal path between source and destination servers.
     * 
     * @param sourceServer Source server ID
     * @param destServer Destination server ID
     * @return RoutingResult containing the optimal path and total latency
     */
    public RoutingResult findOptimalPath(int sourceServer, int destServer) {
        // Special case: if source and destination are the same
        if (sourceServer == destServer) {
            return new RoutingResult(new int[]{sourceServer}, 0);
        }
        
        // Use Dijkstra's algorithm to find the shortest path
        Map<Integer, Integer> distances = new HashMap<>();
        Map<Integer, Integer> previous = new HashMap<>();
        PriorityQueue<int[]> priorityQueue = new PriorityQueue<>(
            Comparator.comparingInt(a -> a[1])
        );
        
        // Initialize distances to infinity for all nodes except the source
        for (int i = 0; i < numServers; i++) {
            distances.put(i, Integer.MAX_VALUE);
        }
        distances.put(sourceServer, 0);
        
        // Add source to priority queue (node id, distance)
        priorityQueue.offer(new int[]{sourceServer, 0});
        
        // Process nodes in order of increasing distance
        while (!priorityQueue.isEmpty()) {
            int[] current = priorityQueue.poll();
            int currentNode = current[0];
            int currentDist = current[1];
            
            // If we've reached our destination, we're done
            if (currentNode == destServer) {
                break;
            }
            
            // Skip if we've found a better path already
            if (currentDist > distances.get(currentNode)) {
                continue;
            }
            
            // Check all neighbors
            for (Map.Entry<Integer, Integer> neighbor : graph.get(currentNode).entrySet()) {
                int nextNode = neighbor.getKey();
                
                // Calculate effective latency considering congestion (bonus feature)
                int latency = neighbor.getValue();
                int congestionFactor = getCongestionFactor(currentNode, nextNode);
                int effectiveLatency = latency + congestionFactor;
                
                // Calculate new potential distance
                int newDist = currentDist + effectiveLatency;
                
                // If this path is better than any we've seen so far to this neighbor
                if (newDist < distances.get(nextNode)) {
                    distances.put(nextNode, newDist);
                    previous.put(nextNode, currentNode);
                    priorityQueue.offer(new int[]{nextNode, newDist});
                }
            }
        }
        
        // Check if a path was found
        if (!previous.containsKey(destServer) && sourceServer != destServer) {
            return new RoutingResult(null, Double.POSITIVE_INFINITY);
        }
        
        // Reconstruct the path
        List<Integer> path = new ArrayList<>();
        Integer current = destServer;
        
        while (current != null) {
            path.add(current);
            current = previous.get(current);
        }
        
        // Reverse the path to get source to destination order
        Collections.reverse(path);
        
        // Update traffic volume on each link in the path (for congestion awareness)
        updateTrafficVolume(path);
        
        // Convert to array and return result
        int[] pathArray = path.stream().mapToInt(Integer::intValue).toArray();
        return new RoutingResult(pathArray, distances.get(destServer));
    }
    
    /**
     * Update traffic volume on each link in the path.
     * This is used for congestion awareness.
     * 
     * @param path List of server IDs representing the path
     */
    private void updateTrafficVolume(List<Integer> path) {
        for (int i = 0; i < path.size() - 1; i++) {
            int server1 = path.get(i);
            int server2 = path.get(i + 1);
            
            // Increment traffic volume on this link
            trafficVolume.get(server1).put(server2, trafficVolume.get(server1).getOrDefault(server2, 0) + 1);
            trafficVolume.get(server2).put(server1, trafficVolume.get(server2).getOrDefault(server1, 0) + 1);
        }
    }
    
    /**
     * Calculate congestion factor for a link based on current traffic volume.
     * This is used for congestion awareness.
     * 
     * @param server1 First server ID
     * @param server2 Second server ID
     * @return Congestion factor to add to the base latency
     */
    private int getCongestionFactor(int server1, int server2) {
        // Simple congestion model: each increment of traffic adds a small penalty
        int traffic = trafficVolume.get(server1).getOrDefault(server2, 0);
        // Logarithmic scaling to prevent excessive penalties
        return (int) Math.log1p(traffic);
    }
    
    /**
     * Detect if the network has become partitioned (bonus feature).
     * 
     * @return true if the network is partitioned, false otherwise
     */
    public boolean isNetworkPartitioned() {
        // Use BFS to check if all nodes are connected
        boolean[] visited = new boolean[numServers];
        Queue<Integer> queue = new LinkedList<>();
        
        // Start from node 0
        queue.offer(0);
        visited[0] = true;
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            
            for (int neighbor : graph.get(current).keySet()) {
                if (!visited[neighbor]) {
                    visited[neighbor] = true;
                    queue.offer(neighbor);
                }
            }
        }
        
        // Check if all nodes were visited
        for (boolean nodeVisited : visited) {
            if (!nodeVisited) {
                return true; // Network is partitioned
            }
        }
        
        return false; // Network is not partitioned
    }
    
    /**
     * Get all servers that are reachable from a given server.
     * This is useful for detecting network partitions.
     * 
     * @param server Server ID to start from
     * @return Set of reachable server IDs
     */
    public Set<Integer> getReachableServers(int server) {
        Set<Integer> reachable = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        
        // Start BFS from the given server
        queue.offer(server);
        reachable.add(server);
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            
            for (int neighbor : graph.get(current).keySet()) {
                if (!reachable.contains(neighbor)) {
                    reachable.add(neighbor);
                    queue.offer(neighbor);
                }
            }
        }
        
        return reachable;
    }
    
    /**
     * Get the current network topology as an adjacency list.
     * 
     * @return Map representing the network topology
     */
    public Map<Integer, Map<Integer, Integer>> getNetworkTopology() {
        // Create a deep copy to prevent external modification
        Map<Integer, Map<Integer, Integer>> topologyCopy = new HashMap<>();
        
        for (Map.Entry<Integer, Map<Integer, Integer>> entry : graph.entrySet()) {
            topologyCopy.put(entry.getKey(), new HashMap<>(entry.getValue()));
        }
        
        return topologyCopy;
    }
}