import java.util.*;

public class TaskScheduler {

    public int findMinMaxLateness(int N, int[] duration, int[] deadline, List<List<Integer>> dependencies) {
        // Build the graph and compute in-degrees.
        List<List<Integer>> graph = new ArrayList<>();
        int[] indegree = new int[N];
        for (int i = 0; i < N; i++) {
            graph.add(new ArrayList<>());
        }
        for (int i = 0; i < N; i++) {
            List<Integer> deps = dependencies.get(i);
            for (int dep : deps) {
                // There is an edge from dep to i.
                graph.get(dep).add(i);
                indegree[i]++;
            }
        }

        // Binary search for the minimum slack L that makes the schedule feasible.
        // If L is 0, it means we can schedule all tasks to finish by their deadlines.
        long low = 0;
        long high = 0;
        for (int t : duration) {
            high += t;
        }
        long ans = high;
        boolean feasibleFound = false;
        while (low <= high) {
            long mid = low + (high - low) / 2;
            if (isFeasible(N, duration, deadline, graph, indegree, mid)) {
                feasibleFound = true;
                ans = mid;
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        
        // Return 0 if tasks can be scheduled to meet deadlines, else -1.
        return (ans == 0) ? 0 : -1;
    }

    private boolean isFeasible(int N, int[] duration, int[] deadline, List<List<Integer>> graph, int[] originalIndegree, long L) {
        // Copy the original indegree array.
        int[] indegree = Arrays.copyOf(originalIndegree, N);
        // Priority queue to select tasks with the earliest deadline first.
        PriorityQueue<Integer> available = new PriorityQueue<>(new Comparator<Integer>() {
            public int compare(Integer a, Integer b) {
                return Integer.compare(deadline[a], deadline[b]);
            }
        });
        
        // Add all tasks with no prerequisites.
        for (int i = 0; i < N; i++) {
            if (indegree[i] == 0) {
                available.offer(i);
            }
        }
        
        long currentTime = 0;
        int count = 0;
        
        while (!available.isEmpty()) {
            int task = available.poll();
            currentTime += duration[task];
            // Check if task finishes within its deadline plus slack L.
            if (currentTime > (long) deadline[task] + L) {
                return false;
            }
            count++;
            // Release dependent tasks.
            for (int neighbor : graph.get(task)) {
                indegree[neighbor]--;
                if (indegree[neighbor] == 0) {
                    available.offer(neighbor);
                }
            }
        }
        
        return count == N;
    }
}