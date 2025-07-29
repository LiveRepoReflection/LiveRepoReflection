import java.util.*;

public class TaskScheduler {

    public List<ScheduledTask> schedule(List<Task> tasks, int numWorkers, int MAX_RETRIES) {
        Map<Integer, Task> pendingTasks = new HashMap<>();
        Map<Integer, Integer> retriesMap = new HashMap<>();
        for (Task task : tasks) {
            pendingTasks.put(task.getId(), task);
            retriesMap.put(task.getId(), 0);
        }
        Set<Integer> completed = new HashSet<>();
        List<ScheduledTask> result = new ArrayList<>();
        int[] workerNextFree = new int[numWorkers];
        Arrays.fill(workerNextFree, 0);
        int currentTime = 0;

        // Run simulation until all tasks are either successfully completed or failed after max retries.
        while (!pendingTasks.isEmpty()) {
            List<Task> readyTasks = new ArrayList<>();
            // Identify tasks whose dependencies are satisfied.
            for (Task task : pendingTasks.values()) {
                boolean ready = true;
                for (int dep : task.getDependencies()) {
                    if (!completed.contains(dep)) {
                        ready = false;
                        break;
                    }
                }
                if (ready) {
                    readyTasks.add(task);
                }
            }
            // If no tasks are ready, there might be a deadlock. Try to resolve it.
            if (readyTasks.isEmpty()) {
                if (!pendingTasks.isEmpty()) {
                    boolean resolved = detectAndResolveDeadlock(pendingTasks);
                    if (!resolved) {
                        // If deadlock is not detected, advance time to the nearest worker availability.
                        int minWorkerTime = Arrays.stream(workerNextFree).min().orElse(currentTime);
                        currentTime = Math.max(currentTime, minWorkerTime);
                    }
                    continue;
                }
            }
            // Sort ready tasks by descending priority; if equal, ascending task id.
            readyTasks.sort((a, b) -> {
                if (b.getPriority() != a.getPriority()) {
                    return b.getPriority() - a.getPriority();
                } else {
                    return a.getId() - b.getId();
                }
            });
            // Schedule each ready task.
            for (Task task : readyTasks) {
                if (!pendingTasks.containsKey(task.getId())) {
                    continue; // Task might have been scheduled in another iteration.
                }
                // Select the worker that becomes available the earliest.
                int workerId = 0;
                int earliest = workerNextFree[0];
                for (int i = 1; i < numWorkers; i++) {
                    if (workerNextFree[i] < earliest) {
                        earliest = workerNextFree[i];
                        workerId = i;
                    }
                }
                currentTime = Math.max(currentTime, workerNextFree[workerId]);
                int startTime = currentTime;
                int endTime = startTime + task.getExecutionTime();

                int currentRetry = retriesMap.get(task.getId());
                boolean success = simulateExecution(task, currentRetry);
                if (success) {
                    completed.add(task.getId());
                    ScheduledTask st = new ScheduledTask(task.getId(), workerId, startTime, endTime, "SUCCESS", currentRetry);
                    result.add(st);
                    pendingTasks.remove(task.getId());
                } else {
                    currentRetry++;
                    retriesMap.put(task.getId(), currentRetry);
                    if (currentRetry > MAX_RETRIES) {
                        ScheduledTask st = new ScheduledTask(task.getId(), workerId, startTime, endTime, "FAILED", currentRetry);
                        result.add(st);
                        pendingTasks.remove(task.getId());
                    }
                    // If not exceeded MAX_RETRIES, the task remains in pendingTasks for rescheduling.
                }
                workerNextFree[workerId] = endTime;
                currentTime = endTime;
            }
        }
        return result;
    }

    private boolean simulateExecution(Task task, int retryCount) {
        // Deterministic simulation:
        // For tasks with an even id, fail on the first attempt (retryCount == 0).
        if (task.getId() % 2 == 0 && retryCount == 0) {
            return false;
        }
        return true;
    }

    private boolean detectAndResolveDeadlock(Map<Integer, Task> pendingTasks) {
        // Build dependency graph for pending tasks.
        Map<Integer, List<Integer>> graph = new HashMap<>();
        for (Task task : pendingTasks.values()) {
            List<Integer> deps = new ArrayList<>();
            for (int dep : task.getDependencies()) {
                if (pendingTasks.containsKey(dep)) {
                    deps.add(dep);
                }
            }
            graph.put(task.getId(), deps);
        }
        Set<Integer> visited = new HashSet<>();
        Set<Integer> recStack = new HashSet<>();
        List<Integer> cycleNodes = new ArrayList<>();
        for (int node : graph.keySet()) {
            if (detectCycleUtil(node, graph, visited, recStack, cycleNodes)) {
                // Cycle detected: Identify the task with the lowest priority in the cycle.
                int candidateId = cycleNodes.get(0);
                Task candidateTask = pendingTasks.get(candidateId);
                for (int id : cycleNodes) {
                    Task t = pendingTasks.get(id);
                    if (t.getPriority() < candidateTask.getPriority() ||
                       (t.getPriority() == candidateTask.getPriority() && t.getId() < candidateId)) {
                        candidateId = t.getId();
                        candidateTask = t;
                    }
                }
                // Remove one dependency from the candidate task that is part of the cycle.
                List<Integer> deps = candidateTask.getDependencies();
                int removeDep = Integer.MAX_VALUE;
                for (int dep : deps) {
                    if (cycleNodes.contains(dep) && dep < removeDep) {
                        removeDep = dep;
                    }
                }
                if (removeDep != Integer.MAX_VALUE) {
                    deps.remove((Integer) removeDep);
                    return true;
                }
            }
        }
        return false;
    }

    private boolean detectCycleUtil(int node, Map<Integer, List<Integer>> graph, Set<Integer> visited, Set<Integer> recStack, List<Integer> cycleNodes) {
        if (recStack.contains(node)) {
            cycleNodes.add(node);
            return true;
        }
        if (visited.contains(node)) {
            return false;
        }
        visited.add(node);
        recStack.add(node);
        List<Integer> neighbors = graph.getOrDefault(node, new ArrayList<>());
        for (int neighbor : neighbors) {
            if (detectCycleUtil(neighbor, graph, visited, recStack, cycleNodes)) {
                cycleNodes.add(node);
                return true;
            }
        }
        recStack.remove(node);
        return false;
    }
}