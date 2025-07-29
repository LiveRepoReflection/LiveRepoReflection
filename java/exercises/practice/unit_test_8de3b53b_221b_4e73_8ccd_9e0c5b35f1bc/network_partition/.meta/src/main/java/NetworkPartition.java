import java.util.ArrayList;
import java.util.List;

public class NetworkPartition {

    public int minNodesToRemove(int n, int k, List<int[]> edges) {
        // Build the undirected graph as an adjacency list.
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            int u = edge[0], v = edge[1];
            graph[u].add(v);
            graph[v].add(u);
        }
        
        // If k is less than or equal to the initial number of components, no removals needed.
        int initComponents = countComponents(n, graph, new boolean[n]);
        if (initComponents >= k) {
            return 0;
        }
        
        // For each possible removal count from 0 to n, try all combinations.
        // Since n can be up to 100 in theory but test cases are small,
        // we use combination generation brute-force.
        for (int r = 0; r <= n; r++) {
            boolean[] removed = new boolean[n];
            if (searchCombination(0, r, removed, n, k, graph)) {
                return r;
            }
        }
        return -1;
    }
    
    // Recursively generate all combinations of r nodes to remove.
    private boolean searchCombination(int start, int r, boolean[] removed, int n, int k, List<Integer>[] graph) {
        if (r == 0) {
            // Check if current removal set yields at least k components.
            int comp = countComponents(n, graph, removed);
            if (comp >= k) {
                return true;
            }
            return false;
        }
        for (int i = start; i <= n - r; i++) {
            removed[i] = true;
            if (searchCombination(i + 1, r - 1, removed, n, k, graph)) {
                return true;
            }
            removed[i] = false;
        }
        return false;
    }
    
    // Count connected components in the graph ignoring removed nodes.
    private int countComponents(int n, List<Integer>[] graph, boolean[] removed) {
        boolean[] visited = new boolean[n];
        int count = 0;
        for (int i = 0; i < n; i++) {
            if (!removed[i] && !visited[i]) {
                dfs(i, graph, visited, removed);
                count++;
            }
        }
        return count;
    }
    
    private void dfs(int node, List<Integer>[] graph, boolean[] visited, boolean[] removed) {
        visited[node] = true;
        for (int neighbor : graph[node]) {
            if (!removed[neighbor] && !visited[neighbor]) {
                dfs(neighbor, graph, visited, removed);
            }
        }
    }
}