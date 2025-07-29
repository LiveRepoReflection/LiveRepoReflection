import java.util.*;

public class TaskScheduler {

    public static int minimizeMaxLateness(int N, List<Task> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return 0;
        }

        // Sort tasks by deadline (Earliest Deadline First)
        List<Task> sortedTasks = new ArrayList<>(tasks);
        sortedTasks.sort(Comparator.comparingInt(t -> t.deadline));

        // Binary search for minimum possible maximum lateness.
        int low = -10000;  // Lower bound for lateness (can be negative if tasks complete early)
        int high = 100000; // Upper bound (loose bound based on given constraints)

        while (low < high) {
            int mid = low + (high - low) / 2;
            if (isFeasible(N, sortedTasks, mid)) {
                high = mid;
            } else {
                low = mid + 1;
            }
        }
        return low;
    }

    private static boolean isFeasible(int N, List<Task> tasks, int L) {
        // For each machine, maintain its current finish time.
        int[] machines = new int[N];
        Arrays.fill(machines, 0);

        // Greedily assign each task to a machine where it can complete with lateness <= L.
        for (Task task : tasks) {
            int bestMachine = -1;
            int bestFinishTime = Integer.MAX_VALUE;
            for (int i = 0; i < N; i++) {
                int finishTime = machines[i] + task.executionTime;
                // Check if this machine can finish the task within the allowed time.
                if (finishTime <= task.deadline + L && finishTime < bestFinishTime) {
                    bestFinishTime = finishTime;
                    bestMachine = i;
                }
            }
            if (bestMachine == -1) {
                return false;
            }
            machines[bestMachine] = bestFinishTime;
        }
        return true;
    }
}