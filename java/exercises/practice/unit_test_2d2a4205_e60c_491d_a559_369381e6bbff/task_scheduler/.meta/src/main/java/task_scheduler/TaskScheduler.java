package task_scheduler;

import java.util.*;

public class TaskScheduler {

    public List<Integer> getOptimalSchedule(List<Task> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return new ArrayList<>();
        }

        // Build a mapping from task id to Task object.
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.getId(), task);
        }

        // Build the graph for dependency relationships.
        // inDegree maps task id to number of prerequisites.
        // graph maps each task id to a list of tasks that depend on it.
        Map<Integer, Integer> inDegree = new HashMap<>();
        Map<Integer, List<Integer>> graph = new HashMap<>();
        for (Task task : tasks) {
            inDegree.put(task.getId(), 0);
            graph.put(task.getId(), new ArrayList<>());
        }

        // Populate graph and inDegree counts.
        for (Task task : tasks) {
            for (Integer depId : task.getDependencies()) {
                // If a dependency does not exist in the provided task list, input is invalid.
                if (!taskMap.containsKey(depId)) {
                    return new ArrayList<>();
                }
                graph.get(depId).add(task.getId());
                inDegree.put(task.getId(), inDegree.get(task.getId()) + 1);
            }
        }

        // Use a priority queue to process tasks with zero in-degree.
        // The comparator sorts tasks by their deadlines (ascending).
        PriorityQueue<Task> availableTasks = new PriorityQueue<>(new Comparator<Task>() {
            @Override
            public int compare(Task t1, Task t2) {
                return Integer.compare(t1.getDeadline(), t2.getDeadline());
            }
        });

        // Add all tasks with no dependencies.
        for (Task task : tasks) {
            if (inDegree.get(task.getId()) == 0) {
                availableTasks.offer(task);
            }
        }

        List<Integer> schedule = new ArrayList<>();
        int currentTime = 0;

        while (!availableTasks.isEmpty()) {
            Task current = availableTasks.poll();
            schedule.add(current.getId());
            currentTime += current.getDuration();
            
            // Process tasks dependent on the current task.
            for (Integer neighborId : graph.get(current.getId())) {
                inDegree.put(neighborId, inDegree.get(neighborId) - 1);
                if (inDegree.get(neighborId) == 0) {
                    availableTasks.offer(taskMap.get(neighborId));
                }
            }
        }

        // If the schedule does not include all tasks, a cycle exists.
        if (schedule.size() != tasks.size()) {
            return new ArrayList<>();
        }

        // The resulting schedule is a valid topological order that prioritizes tasks with earlier deadlines.
        return schedule;
    }
}