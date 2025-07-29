import java.util.*;
import java.util.stream.Collectors;

public class TaskScheduler {
    public static List<Integer> scheduleTasks(List<Task> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return Collections.emptyList();
        }

        // Check for circular dependencies
        if (hasCircularDependencies(tasks)) {
            return Collections.emptyList();
        }

        // Build dependency graph and in-degree count
        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        Map<Integer, Task> taskMap = new HashMap<>();

        for (Task task : tasks) {
            taskMap.put(task.getId(), task);
            graph.putIfAbsent(task.getId(), new ArrayList<>());
            inDegree.putIfAbsent(task.getId(), 0);
        }

        for (Task task : tasks) {
            for (int depId : task.getDependencies()) {
                graph.get(depId).add(task.getId());
                inDegree.put(task.getId(), inDegree.getOrDefault(task.getId(), 0) + 1);
            }
        }

        // Kahn's algorithm for topological sort
        Queue<Integer> queue = new PriorityQueue<>(
            Comparator.comparingInt(id -> taskMap.get(id).getDeadline())
        );

        for (Map.Entry<Integer, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.add(entry.getKey());
            }
        }

        List<Integer> result = new ArrayList<>();
        int currentTime = 0;
        Map<Integer, Integer> completionTimes = new HashMap<>();

        while (!queue.isEmpty()) {
            int taskId = queue.poll();
            Task task = taskMap.get(taskId);

            // Check if we can complete this task before deadline
            int finishTime = currentTime + task.getDuration();
            if (finishTime <= task.getDeadline()) {
                result.add(taskId);
                completionTimes.put(taskId, finishTime);
                currentTime = finishTime;
            }

            // Process dependencies
            for (int neighbor : graph.get(taskId)) {
                inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                if (inDegree.get(neighbor) == 0) {
                    queue.add(neighbor);
                }
            }
        }

        // Try to schedule missed tasks if possible
        List<Task> missedTasks = tasks.stream()
            .filter(t -> !result.contains(t.getId()))
            .sorted(Comparator.comparingInt(Task::getDeadline))
            .collect(Collectors.toList());

        for (Task task : missedTasks) {
            boolean allDepsCompleted = task.getDependencies().stream()
                .allMatch(completionTimes::containsKey);

            if (allDepsCompleted) {
                int startTime = task.getDependencies().stream()
                    .mapToInt(completionTimes::get)
                    .max()
                    .orElse(currentTime);

                int finishTime = startTime + task.getDuration();
                if (finishTime <= task.getDeadline()) {
                    result.add(task.getId());
                    completionTimes.put(task.getId(), finishTime);
                    currentTime = finishTime;
                }
            }
        }

        return result;
    }

    private static boolean hasCircularDependencies(List<Task> tasks) {
        Map<Integer, List<Integer>> graph = new HashMap<>();
        for (Task task : tasks) {
            graph.put(task.getId(), new ArrayList<>(task.getDependencies()));
        }

        Set<Integer> visited = new HashSet<>();
        Set<Integer> recursionStack = new HashSet<>();

        for (Integer taskId : graph.keySet()) {
            if (isCyclic(taskId, graph, visited, recursionStack)) {
                return true;
            }
        }
        return false;
    }

    private static boolean isCyclic(Integer taskId, Map<Integer, List<Integer>> graph, 
                                  Set<Integer> visited, Set<Integer> recursionStack) {
        if (recursionStack.contains(taskId)) {
            return true;
        }
        if (visited.contains(taskId)) {
            return false;
        }

        visited.add(taskId);
        recursionStack.add(taskId);

        for (Integer neighbor : graph.getOrDefault(taskId, Collections.emptyList())) {
            if (isCyclic(neighbor, graph, visited, recursionStack)) {
                return true;
            }
        }

        recursionStack.remove(taskId);
        return false;
    }
}