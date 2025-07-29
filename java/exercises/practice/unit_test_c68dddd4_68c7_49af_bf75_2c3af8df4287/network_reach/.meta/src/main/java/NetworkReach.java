import java.util.*;

public class NetworkReach {
    private Map<Integer, Set<Integer>> graph;
    private Map<Integer, Set<Integer>> reachabilityCache;
    
    public NetworkReach() {
        graph = new HashMap<>();
        reachabilityCache = new HashMap<>();
    }
    
    public void add_friendship(int user1, int user2) {
        graph.computeIfAbsent(user1, k -> new HashSet<>()).add(user2);
        // Ensure user2 exists in the graph even if it doesn't have outgoing edges.
        graph.computeIfAbsent(user2, k -> new HashSet<>());
        // Invalidate cache because the graph structure has changed.
        reachabilityCache.clear();
    }
    
    public boolean is_reachable(int user1, int user2) {
        if (user1 == user2) {
            return true;
        }
        if (!graph.containsKey(user1)) {
            return false;
        }
        // Use cached result if available.
        if (reachabilityCache.containsKey(user1)) {
            return reachabilityCache.get(user1).contains(user2);
        }
        // Compute reachable nodes using BFS.
        Set<Integer> reachable = new HashSet<>();
        Queue<Integer> queue = new LinkedList<>();
        queue.offer(user1);
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            Set<Integer> neighbors = graph.getOrDefault(current, Collections.emptySet());
            for (int neighbor : neighbors) {
                if (!reachable.contains(neighbor)) {
                    reachable.add(neighbor);
                    queue.offer(neighbor);
                }
            }
        }
        // Cache the computed reachable set.
        reachabilityCache.put(user1, reachable);
        return reachable.contains(user2);
    }
}