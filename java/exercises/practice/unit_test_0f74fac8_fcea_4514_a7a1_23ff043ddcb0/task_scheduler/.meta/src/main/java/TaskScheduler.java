import java.util.*;
import java.lang.reflect.Field;

public class TaskScheduler {

    // Inner class representing a task in the scheduling simulation.
    private static class TaskNode {
        int id;
        int duration;
        List<Integer> dependencies;
        Map<String, Integer> resourceRequirements;
        List<TaskNode> dependents;
        int inDegree;
        int startTime;

        TaskNode(int id, int duration, List<Integer> dependencies, Map<String, Integer> resourceRequirements) {
            this.id = id;
            this.duration = duration;
            this.dependencies = dependencies;
            this.resourceRequirements = resourceRequirements;
            this.dependents = new ArrayList<>();
            this.inDegree = 0;
            this.startTime = -1;
        }
    }

    // Running task event for simulation
    private static class RunningTask {
        TaskNode task;
        int finishTime;

        RunningTask(TaskNode task, int finishTime) {
            this.task = task;
            this.finishTime = finishTime;
        }
    }

    /**
     * Schedules tasks given a list of task objects and available resources.
     * Each task object is expected to have the following fields:
     *  - int id;
     *  - int duration;
     *  - List<Integer> dependencies;
     *  - Map<String, Integer> resourceRequirements;
     *
     * The method returns a Map where the key is the task id and the value is its scheduled start time.
     * If a feasible schedule does not exist, an empty map is returned.
     */
    public static Map<Integer, Integer> scheduleTasks(List<?> tasks, Map<String, Integer> availableResources) {
        // Convert input tasks using reflection to our internal representation.
        Map<Integer, TaskNode> nodes = new HashMap<>();
        for (Object obj : tasks) {
            try {
                // Access the fields using reflection.
                Field idField = obj.getClass().getDeclaredField("id");
                idField.setAccessible(true);
                int id = (int) idField.get(obj);
                
                Field durationField = obj.getClass().getDeclaredField("duration");
                durationField.setAccessible(true);
                int duration = (int) durationField.get(obj);
                
                Field depsField = obj.getClass().getDeclaredField("dependencies");
                depsField.setAccessible(true);
                @SuppressWarnings("unchecked")
                List<Integer> dependencies = (List<Integer>) depsField.get(obj);
                
                Field resField = obj.getClass().getDeclaredField("resourceRequirements");
                resField.setAccessible(true);
                @SuppressWarnings("unchecked")
                Map<String, Integer> resourceRequirements = (Map<String, Integer>) resField.get(obj);

                // Check if any task has a requirement that exceeds the available resource.
                for (Map.Entry<String, Integer> req : resourceRequirements.entrySet()) {
                    int available = availableResources.getOrDefault(req.getKey(), 0);
                    if (req.getValue() > available) {
                        return new HashMap<>();
                    }
                }
                
                TaskNode node = new TaskNode(id, duration, dependencies, resourceRequirements);
                nodes.put(id, node);
            } catch (Exception e) {
                // In case of any reflection error, return empty schedule.
                return new HashMap<>();
            }
        }

        // Build dependency graph. Also check for missing dependency ids.
        for (TaskNode node : nodes.values()) {
            for (int depId : node.dependencies) {
                if (!nodes.containsKey(depId)) {
                    return new HashMap<>();
                }
                // Avoid self dependency.
                if (depId == node.id && node.dependencies.size() > 0) {
                    return new HashMap<>();
                }
                TaskNode depNode = nodes.get(depId);
                depNode.dependents.add(node);
                node.inDegree++;
            }
        }

        // Check for cycle using count of tasks processed.
        int totalTasks = nodes.size();
        int countCheck = 0;
        Queue<TaskNode> cycleCheckQueue = new LinkedList<>();
        for (TaskNode node : nodes.values()) {
            if (node.inDegree == 0) {
                cycleCheckQueue.offer(node);
            }
        }
        while (!cycleCheckQueue.isEmpty()) {
            TaskNode cur = cycleCheckQueue.poll();
            countCheck++;
            for (TaskNode dependent : cur.dependents) {
                dependent.inDegree--;
                if (dependent.inDegree == 0) {
                    cycleCheckQueue.offer(dependent);
                }
            }
        }
        if (countCheck != totalTasks) {
            // There is a cycle.
            return new HashMap<>();
        }

        // Reinitialize inDegree for simulation.
        for (TaskNode node : nodes.values()) {
            node.inDegree = node.dependencies.size();
        }

        // Simulation details:
        int currentTime = 0;
        // Used resources at the current time by running tasks.
        Map<String, Integer> usedResources = new HashMap<>();
        for (String key : availableResources.keySet()) {
            usedResources.put(key, 0);
        }
        // PriorityQueue for running tasks ordered by finish time.
        PriorityQueue<RunningTask> runningPQ = new PriorityQueue<>(Comparator.comparingInt(rt -> rt.finishTime));
        // Ready tasks PriorityQueue ordered by descending duration (longest first).
        PriorityQueue<TaskNode> readyPQ = new PriorityQueue<>((a, b) -> Integer.compare(b.duration, a.duration));

        // Initialize ready list: tasks with no dependencies.
        for (TaskNode node : nodes.values()) {
            if (node.inDegree == 0) {
                readyPQ.offer(node);
            }
        }

        // Map to store result schedule.
        Map<Integer, Integer> schedule = new HashMap<>();

        // Count scheduled tasks.
        int scheduledTasks = 0;

        while (scheduledTasks < totalTasks) {
            boolean scheduledNewTask = false;
            // Try to schedule ready tasks that satisfy resource constraints.
            List<TaskNode> deferred = new ArrayList<>();
            while (!readyPQ.isEmpty()) {
                TaskNode candidate = readyPQ.poll();
                if (canAllocate(candidate, availableResources, usedResources)) {
                    // Allocate resources for the task.
                    allocateResources(candidate, usedResources);
                    candidate.startTime = currentTime;
                    schedule.put(candidate.id, currentTime);
                    scheduledNewTask = true;
                    scheduledTasks++;
                    // Add to running tasks.
                    runningPQ.offer(new RunningTask(candidate, currentTime + candidate.duration));
                } else {
                    deferred.add(candidate);
                }
            }
            // Put back deferred tasks.
            for (TaskNode node : deferred) {
                readyPQ.offer(node);
            }

            if (!scheduledNewTask) {
                if (runningPQ.isEmpty()) {
                    // No tasks can be scheduled and none are running.
                    return new HashMap<>();
                }
                // Advance time to next finish event.
                RunningTask finishedTask = runningPQ.poll();
                int nextTime = finishedTask.finishTime;
                // Advance current time.
                currentTime = nextTime;
                // Release resources for all tasks that finish at this time.
                List<RunningTask> finishedAtTheSameTime = new ArrayList<>();
                finishedAtTheSameTime.add(finishedTask);
                while (!runningPQ.isEmpty() && runningPQ.peek().finishTime == currentTime) {
                    finishedAtTheSameTime.add(runningPQ.poll());
                }
                for (RunningTask rt : finishedAtTheSameTime) {
                    releaseResources(rt.task, usedResources);
                    // Update dependent tasks.
                    for (TaskNode dependent : rt.task.dependents) {
                        dependent.inDegree--;
                        if (dependent.inDegree == 0) {
                            readyPQ.offer(dependent);
                        }
                    }
                }
            }
        }
        return schedule;
    }

    // Helper method to check if task resources can be allocated.
    private static boolean canAllocate(TaskNode task, Map<String, Integer> available, Map<String, Integer> used) {
        for (Map.Entry<String, Integer> req : task.resourceRequirements.entrySet()) {
            int availableAmount = available.getOrDefault(req.getKey(), 0);
            int usedAmount = used.getOrDefault(req.getKey(), 0);
            if (usedAmount + req.getValue() > availableAmount) {
                return false;
            }
        }
        return true;
    }

    // Helper method to allocate resources.
    private static void allocateResources(TaskNode task, Map<String, Integer> used) {
        for (Map.Entry<String, Integer> req : task.resourceRequirements.entrySet()) {
            used.put(req.getKey(), used.getOrDefault(req.getKey(), 0) + req.getValue());
        }
    }

    // Helper method to release resources.
    private static void releaseResources(TaskNode task, Map<String, Integer> used) {
        for (Map.Entry<String, Integer> req : task.resourceRequirements.entrySet()) {
            used.put(req.getKey(), used.getOrDefault(req.getKey(), 0) - req.getValue());
        }
    }
}