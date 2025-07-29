package task_scheduler;

import java.util.*;

public class Scheduler {
    public static int calculateMinimumTotalLateness(List<Task> tasks) {
        // Map task id to Task object.
        Map<Integer, Task> taskMap = new HashMap<>();
        // Graph: dependency edges from a task to tasks that depend on it.
        Map<Integer, List<Integer>> graph = new HashMap<>();
        // Count of incoming edges for each task.
        Map<Integer, Integer> indegree = new HashMap<>();

        for (Task task : tasks) {
            int id = task.getId();
            taskMap.put(id, task);
            indegree.put(id, 0);
            graph.put(id, new ArrayList<>());
        }

        // Build graph: for each task, for each dependency, add an edge from dependency to the task.
        for (Task task : tasks) {
            int id = task.getId();
            for (int dep : task.getDependencies()) {
                if (!taskMap.containsKey(dep)) {
                    throw new IllegalArgumentException("Invalid dependency: " + dep);
                }
                graph.get(dep).add(id);
                indegree.put(id, indegree.get(id) + 1);
            }
        }

        // Use a priority queue to select the available task with the earliest deadline.
        PriorityQueue<Task> available = new PriorityQueue<>(Comparator
                .comparingInt(Task::getDeadline)
                .thenComparingInt(Task::getId));

        for (Map.Entry<Integer, Integer> entry : indegree.entrySet()) {
            if (entry.getValue() == 0) {
                available.offer(taskMap.get(entry.getKey()));
            }
        }

        int currentTime = 0;
        int scheduledCount = 0;
        while (!available.isEmpty()) {
            Task currentTask = available.poll();
            currentTime += currentTask.getDuration();
            // If a task finishes after its deadline, return -1.
            if (currentTime > currentTask.getDeadline()) {
                return -1;
            }
            scheduledCount++;
            // Reduce the indegree of dependent tasks.
            for (int neighbor : graph.get(currentTask.getId())) {
                indegree.put(neighbor, indegree.get(neighbor) - 1);
                if (indegree.get(neighbor) == 0) {
                    available.offer(taskMap.get(neighbor));
                }
            }
        }

        // In case not all tasks are scheduled (cycle exists, for example)
        if (scheduledCount != tasks.size()) {
            return -1;
        }

        // If all tasks are scheduled within their deadlines, total lateness is 0.
        return 0;
    }
}