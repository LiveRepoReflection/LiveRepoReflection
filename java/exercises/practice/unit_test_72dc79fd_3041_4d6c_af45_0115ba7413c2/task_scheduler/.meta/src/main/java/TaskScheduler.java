import java.util.*;

public class TaskScheduler {

    // Global variable for backtracking optimum result
    private static long bestTotalLateness;

    public static int minTotalLateness(List<Task> tasks) {
        int n = tasks.size();
        // Build task map by id for quick access.
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.id, t);
        }

        // Build graph: for each task, add to successors of its dependencies.
        // Also, compute in-degree for each task.
        Map<Integer, Integer> inDegree = new HashMap<>();
        for (Task t : tasks) {
            inDegree.put(t.id, t.dependencies.size());
        }
        for (Task t : tasks) {
            for (int dep : t.dependencies) {
                Task depTask = taskMap.get(dep);
                if (depTask != null) {
                    depTask.successors.add(t);
                }
            }
        }

        // For small number of tasks, use exhaustive backtracking to guarantee optimality.
        if(n <= 15) {
            bestTotalLateness = Long.MAX_VALUE;
            // Initialize available tasks: tasks with inDegree zero.
            List<Task> available = new ArrayList<>();
            for (Task t : tasks) {
                if (inDegree.get(t.id) == 0) {
                    available.add(t);
                }
            }
            // Make a copy of inDegree map for backtracking.
            backtrack(0, 0, inDegree, available, taskMap);
            return (int) bestTotalLateness;
        } else {
            // For larger set of tasks, use a greedy heuristic:
            // At each step, select from available tasks (in-degree 0) the task with earliest deadline.
            PriorityQueue<Task> queue = new PriorityQueue<>(Comparator.comparingInt(t -> t.deadline));
            for (Task t : tasks) {
                if (inDegree.get(t.id) == 0) {
                    queue.offer(t);
                }
            }
            long currentTime = 0;
            long totalLateness = 0;
            while (!queue.isEmpty()) {
                Task curr = queue.poll();
                currentTime += curr.duration;
                totalLateness += Math.max(0, currentTime - curr.deadline);

                // For each successor, reduce in-degree and add if becomes 0.
                for (Task succ : curr.successors) {
                    int deg = inDegree.get(succ.id) - 1;
                    inDegree.put(succ.id, deg);
                    if (deg == 0) {
                        queue.offer(succ);
                    }
                }
            }
            return (int) totalLateness;
        }
    }

    // Backtracking for optimal scheduling for small number of tasks.
    private static void backtrack(long currentTime, long currentLate, Map<Integer, Integer> inDegree, List<Task> available, Map<Integer, Task> taskMap) {
        // If no tasks are left, update best result.
        if (available.isEmpty()) {
            // Check if all tasks have been scheduled.
            boolean allScheduled = true;
            for (int deg : inDegree.values()) {
                if (deg != -1) { // We mark scheduled tasks with -1.
                    allScheduled = false;
                    break;
                }
            }
            if (allScheduled) {
                bestTotalLateness = Math.min(bestTotalLateness, currentLate);
            }
            return;
        }

        // Prune if current lateness already exceeds best found.
        if (currentLate >= bestTotalLateness) {
            return;
        }

        // Try each available task in turn.
        // To avoid side-effects, make a copy of available list for each recursive call.
        for (int i = 0; i < available.size(); i++) {
            Task task = available.get(i);

            // Prepare new available list for next recursion.
            List<Task> nextAvailable = new ArrayList<>(available);
            nextAvailable.remove(i);

            // Save state changes: copy inDegree map.
            Map<Integer, Integer> newInDegree = new HashMap<>(inDegree);
            // Mark current task as scheduled.
            newInDegree.put(task.id, -1);

            long finishTime = currentTime + task.duration;
            long lateness = Math.max(0, finishTime - task.deadline);
            long nextLate = currentLate + lateness;

            // For each successor, decrement in-degree and if becomes 0, add to available.
            for (Task succ : task.successors) {
                if (newInDegree.get(succ.id) != -1) { // if not already scheduled
                    int newDeg = newInDegree.get(succ.id) - 1;
                    newInDegree.put(succ.id, newDeg);
                    if (newDeg == 0) {
                        nextAvailable.add(succ);
                    }
                }
            }
            backtrack(finishTime, nextLate, newInDegree, nextAvailable, taskMap);
        }
    }
}