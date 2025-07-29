import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

public class TaskScheduler {
    public static List<Integer> scheduleTasks(List<Task> tasks) {
        if (tasks.isEmpty()) {
            return Collections.emptyList();
        }

        // Build dependency graph and in-degree count
        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        Map<Integer, Task> taskMap = new HashMap<>();
        Map<Integer, Integer> earliestStart = new HashMap<>();

        for (Task task : tasks) {
            int id = task.getId();
            taskMap.put(id, task);
            graph.putIfAbsent(id, new ArrayList<>());
            inDegree.putIfAbsent(id, 0);
            earliestStart.put(id, 0);
        }

        for (Task task : tasks) {
            for (int depId : task.getDependencies()) {
                graph.get(depId).add(task.getId());
                inDegree.put(task.getId(), inDegree.get(task.getId()) + 1);
            }
        }

        // Check for cycles
        if (hasCycle(graph, inDegree)) {
            return Collections.emptyList();
        }

        // Topological sort with earliest start time calculation
        Queue<Integer> queue = new LinkedList<>();
        for (Map.Entry<Integer, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.offer(entry.getKey());
            }
        }

        List<Integer> schedule = new ArrayList<>();
        int currentTime = 0;

        while (!queue.isEmpty()) {
            int size = queue.size();
            List<Integer> currentLevel = new ArrayList<>();

            for (int i = 0; i < size; i++) {
                int taskId = queue.poll();
                currentLevel.add(taskId);
            }

            // Sort tasks in current level by deadline to meet deadlines
            currentLevel.sort((a, b) -> {
                int deadlineA = taskMap.get(a).getDeadline();
                int deadlineB = taskMap.get(b).getDeadline();
                return Integer.compare(deadlineA, deadlineB);
            });

            for (int taskId : currentLevel) {
                Task task = taskMap.get(taskId);
                int startTime = earliestStart.get(taskId);
                int finishTime = startTime + task.getDuration();

                if (finishTime > task.getDeadline()) {
                    return Collections.emptyList();
                }

                schedule.add(taskId);
                currentTime = finishTime;

                for (int neighbor : graph.get(taskId)) {
                    earliestStart.put(neighbor, Math.max(earliestStart.get(neighbor), finishTime));
                    inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                    if (inDegree.get(neighbor) == 0) {
                        queue.offer(neighbor);
                    }
                }
            }
        }

        if (schedule.size() != tasks.size()) {
            return Collections.emptyList();
        }

        return schedule;
    }

    private static boolean hasCycle(Map<Integer, List<Integer>> graph, Map<Integer, Integer> inDegree) {
        Map<Integer, Integer> tempInDegree = new HashMap<>(inDegree);
        Queue<Integer> queue = new LinkedList<>();

        for (Map.Entry<Integer, Integer> entry : tempInDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.offer(entry.getKey());
            }
        }

        int count = 0;
        while (!queue.isEmpty()) {
            int taskId = queue.poll();
            count++;

            for (int neighbor : graph.get(taskId)) {
                tempInDegree.put(neighbor, tempInDegree.get(neighbor) - 1);
                if (tempInDegree.get(neighbor) == 0) {
                    queue.offer(neighbor);
                }
            }
        }

        return count != graph.size();
    }
}