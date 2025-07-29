import java.util.*;

public class TaskOptimizer {

    // Infinity constant for cost comparisons.
    private static final double INF = 1e18;

    public static double getMinimumCost(int n, int m, int[][] skills, int[][] tasks, List<List<Integer>> dependencies, int[] availability, int deadline) {
        // First, compute the longest dependency chain length (L) in the DAG.
        // dp[i] = tasks[i][1] + max_{p in dependencies[i]} dp[p]
        double[] dp = new double[m];
        // For memoizing dp for longest path.
        boolean[] visited = new boolean[m];

        // Build graph: each task i, depends on tasks given in dependencies.get(i)
        // We'll use DFS to compute longest path ending at i.
        double longestChain = 0;
        for (int i = 0; i < m; i++) {
            longestChain = Math.max(longestChain, computeLongestPath(i, tasks, dependencies, dp, visited));
        }
        // If dependency chain itself exceeds deadline, no assignment possible.
        if (longestChain > deadline) {
            return -1.0;
        }

        // Use DFS with memoization over tasks assignment.
        // State: index in tasks array (we process tasks in order 0..m-1) and the current assigned durations for each engineer.
        // We'll assume tasks order is arbitrary, since there is no ordering dependency in assignment.
        int[] used = new int[n]; // current accumulated duration per engineer.
        Map<String, Double> memo = new HashMap<>();
        double ans = dfs(0, n, m, skills, tasks, availability, deadline, used, memo, longestChain);
        return ans >= INF ? -1.0 : ans;
    }

    // DFS over tasks index, assigning each task to an engineer.
    private static double dfs(int i, int n, int m, int[][] skills, int[][] tasks, int[] availability, int deadline, int[] used, Map<String, Double> memo, double longestChain) {
        // Prune if current maximum engineer usage exceeds deadline.
        int currentMax = 0;
        for (int time : used) {
            currentMax = Math.max(currentMax, time);
        }
        if (currentMax > deadline) {
            return INF;
        }
        // If all tasks have been assigned, check overall finish time.
        if (i == m) {
            // Overall finish time is max(currentMax, longestChain).
            int overallFinish = Math.max(currentMax, (int)Math.ceil(longestChain));
            if (overallFinish <= deadline) {
                return 0.0;
            } else {
                return INF;
            }
        }
        
        String key = generateKey(i, used);
        if (memo.containsKey(key)) {
            return memo.get(key);
        }
        double best = INF;
        int cat = tasks[i][0];
        int duration = tasks[i][1];
        // Try assigning task i to each engineer j.
        for (int j = 0; j < n; j++) {
            if (skills[j][cat] <= 0) {
                continue; // Engineer cannot perform this task.
            }
            if (used[j] + duration > availability[j]) {
                continue; // Would exceed engineer availability.
            }
            // Compute cost for assigning task i to engineer j.
            double cost = ((double) duration) / skills[j][cat];
            // Choose engineer j for task i.
            used[j] += duration;
            double next = dfs(i + 1, n, m, skills, tasks, availability, deadline, used, memo, longestChain);
            if (next < INF) {
                best = Math.min(best, cost + next);
            }
            used[j] -= duration; // backtrack
        }
        memo.put(key, best);
        return best;
    }

    // Generate a unique key for memoization based on current task index and used durations array.
    private static String generateKey(int i, int[] used) {
        StringBuilder sb = new StringBuilder();
        sb.append(i);
        sb.append(":");
        for (int time : used) {
            sb.append(time).append(",");
        }
        return sb.toString();
    }

    // Compute longest path ending at task i in the dependency DAG.
    private static double computeLongestPath(int i, int[][] tasks, List<List<Integer>> dependencies, double[] dp, boolean[] visited) {
        if (visited[i]) {
            return dp[i];
        }
        double duration = tasks[i][1];
        double maxDep = 0;
        List<Integer> deps = dependencies.get(i);
        for (int pred : deps) {
            maxDep = Math.max(maxDep, computeLongestPath(pred, tasks, dependencies, dp, visited));
        }
        dp[i] = duration + maxDep;
        visited[i] = true;
        return dp[i];
    }
}