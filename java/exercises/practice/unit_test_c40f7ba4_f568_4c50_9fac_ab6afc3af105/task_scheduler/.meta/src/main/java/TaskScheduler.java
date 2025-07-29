import java.util.Arrays;
import java.util.PriorityQueue;

public class TaskScheduler {

    /**
     * Computes the minimum total penalty incurred by optimally scheduling tasks.
     * Each task i has a deadline deadlines[i], an execution time times[i],
     * and a penalty penalties[i] if not completed by its deadline.
     *
     * Preemption is allowed but a task must be fully completed before its deadline 
     * to avoid the penalty.
     *
     * The approach is to select a subset of tasks to finish on time such that the 
     * total saved penalty is maximized. This is equivalent to minimizing total penalty,
     * where total penalty = sum(all penalties) - sum(saved penalties by tasks completed on time).
     *
     * This method uses a greedy algorithm:
     * 1. Sort tasks by deadline in ascending order.
     * 2. Iteratively add tasks, maintaining the total processing time.
     * 3. If total processing time exceeds the current task's deadline, remove a task
     *    with the lowest penalty efficiency (i.e. smallest penalty per unit time) as it contributes less.
     * 4. The tasks remaining in the priority queue represent the set of tasks completed on time.
     *
     * @param deadlines an array of deadlines for each task.
     * @param times an array of execution times for each task.
     * @param penalties an array of penalties for each task.
     * @return the minimum total penalty incurred.
     */
    public static long minTotalPenalty(int[] deadlines, int[] times, int[] penalties) {
        int n = deadlines.length;
        Task[] tasks = new Task[n];
        long totalPenaltyAll = 0;
        for (int i = 0; i < n; i++) {
            tasks[i] = new Task(deadlines[i], times[i], penalties[i]);
            totalPenaltyAll += penalties[i];
        }

        // Sort tasks by increasing deadline.
        Arrays.sort(tasks, (a, b) -> Integer.compare(a.deadline, b.deadline));

        // PriorityQueue orders tasks by increasing efficiency: penalty per unit time.
        // A task with a lower ratio is less "valuable" per unit time and is removed if needed.
        PriorityQueue<Task> pq = new PriorityQueue<>((a, b) -> {
            // Compare by a.penalty / a.time vs b.penalty / b.time without using division.
            long lhs = (long) a.penalty * b.time;
            long rhs = (long) b.penalty * a.time;
            if (lhs != rhs) {
                return Long.compare(lhs, rhs);
            }
            // If ratios are equal, remove the task with the larger execution time.
            return Integer.compare(a.time, b.time);
        });

        long totalTime = 0;
        long sumCompletedPenalty = 0;
        for (Task task : tasks) {
            pq.offer(task);
            totalTime += task.time;
            sumCompletedPenalty += task.penalty;
            // If the cumulative processing time exceeds the current task's deadline,
            // remove tasks until the set becomes feasible.
            while (totalTime > task.deadline) {
                Task removed = pq.poll();
                totalTime -= removed.time;
                sumCompletedPenalty -= removed.penalty;
            }
        }

        return totalPenaltyAll - sumCompletedPenalty;
    }

    static class Task {
        int deadline;
        int time;
        int penalty;

        Task(int deadline, int time, int penalty) {
            this.deadline = deadline;
            this.time = time;
            this.penalty = penalty;
        }
    }
}