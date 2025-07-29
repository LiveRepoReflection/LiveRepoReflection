import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

public class TaskScheduler {

    public static List<Integer> scheduleTasks(int N, List<Task> tasks) {
        // Map from taskId to Task object for quick lookup
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.taskId, t);
        }

        // Build graph: for each task, record the tasks that depend on it.
        Map<Integer, List<Integer>> graph = new HashMap<>();
        // inDegree: count of prerequisites for each task.
        Map<Integer, Integer> inDegree = new HashMap<>();

        // Initialize graph and inDegree for each task.
        for (Task t : tasks) {
            graph.put(t.taskId, new ArrayList<>());
            inDegree.put(t.taskId, 0);
        }

        // Fill graph and inDegree values.
        for (Task t : tasks) {
            for (Integer dep : t.dependencies) {
                // dep -> t.taskId
                if (graph.containsKey(dep)) {
                    graph.get(dep).add(t.taskId);
                }
                inDegree.put(t.taskId, inDegree.get(t.taskId) + 1);
            }
        }

        // PriorityQueue for available tasks:
        // Comparator: first by deadline, then by duration, then taskId.
        PriorityQueue<Task> available = new PriorityQueue<>((a, b) -> {
            if (a.deadline != b.deadline) {
                return Integer.compare(a.deadline, b.deadline);
            } else if (a.duration != b.duration) {
                return Integer.compare(a.duration, b.duration);
            } else {
                return Integer.compare(a.taskId, b.taskId);
            }
        });

        // Add tasks with inDegree 0 into available pool.
        for (Task t : tasks) {
            if (inDegree.get(t.taskId) == 0) {
                available.add(t);
            }
        }

        List<Integer> schedule = new ArrayList<>();
        int currentTime = 0;
        // Process tasks in order, selecting the one with smallest deadline from the available tasks.
        while (!available.isEmpty()) {
            Task current = available.poll();
            schedule.add(current.taskId);
            currentTime += current.duration;
            // Update all tasks that depend on the current task.
            for (Integer neighborId : graph.get(current.taskId)) {
                inDegree.put(neighborId, inDegree.get(neighborId) - 1);
                if (inDegree.get(neighborId) == 0) {
                    available.add(taskMap.get(neighborId));
                }
            }
        }

        // If we haven't scheduled all tasks, there's a cycle.
        if (schedule.size() != N) {
            return new ArrayList<>();
        }

        return schedule;
    }
}