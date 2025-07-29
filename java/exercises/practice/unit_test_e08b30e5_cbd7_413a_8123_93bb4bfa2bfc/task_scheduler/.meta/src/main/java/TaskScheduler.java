package task_scheduler;

import java.util.*;

public class TaskScheduler {

    public List<Integer> scheduleTasks(int N, int K, int[] taskIds, int[] executionTime, int[] deadlines, List<List<Integer>> dependencies) {
        // Build mapping from taskId to Task
        Map<Integer, Task> taskMap = new HashMap<>();
        for (int i = 0; i < N; i++) {
            Task task = new Task(taskIds[i], executionTime[i], deadlines[i]);
            taskMap.put(taskIds[i], task);
        }

        // Build dependency graph and update dependency count
        for (int i = 0; i < N; i++) {
            int curId = taskIds[i];
            Task curTask = taskMap.get(curId);
            List<Integer> deps = dependencies.get(i);
            for (Integer depId : deps) {
                if (!taskMap.containsKey(depId)) {
                    // Invalid dependency, log warning and ignore
                    System.err.println("Warning: Task " + curId + " has invalid dependency " + depId + " which will be ignored.");
                    continue;
                }
                // Add dependency edge: depId -> curId
                curTask.remainingDependencies++;
                Task depTask = taskMap.get(depId);
                depTask.dependents.add(curTask);
            }
        }

        // Detect cycles using Kahn's algorithm (cycle detection)
        if (hasCycle(taskMap, N)) {
            throw new CyclicDependencyException("Cyclic dependency detected among tasks.");
        }

        // Simulation variables
        long currentTime = 0;
        int availableWorkers = K;

        // Priority queue for tasks available to schedule.
        // Priority: earliest deadline, then smallest executionTime, then smallest task id.
        PriorityQueue<Task> availablePQ = new PriorityQueue<>(new Comparator<Task>() {
            public int compare(Task t1, Task t2) {
                if (t1.deadline != t2.deadline) {
                    return Integer.compare(t1.deadline, t2.deadline);
                } else if (t1.executionTime != t2.executionTime) {
                    return Integer.compare(t1.executionTime, t2.executionTime);
                } else {
                    return Integer.compare(t1.id, t2.id);
                }
            }
        });
        
        // Priority queue for tasks in progress. Sorted by finish time.
        PriorityQueue<Task> inProgressPQ = new PriorityQueue<>(Comparator.comparingLong(t -> t.finishTime));

        // Initialize available tasks which have remainingDependencies = 0
        for (Task task : taskMap.values()) {
            if (task.remainingDependencies == 0) {
                availablePQ.offer(task);
            }
        }
        
        // Process tasks with zero execution time upfront
        while (!availablePQ.isEmpty() && availablePQ.peek().executionTime == 0) {
            Task zeroTask = availablePQ.poll();
            zeroTask.finishTime = currentTime;
            // Mark task complete and update dependents immediately.
            for (Task dependent : zeroTask.dependents) {
                dependent.remainingDependencies--;
                if (dependent.remainingDependencies == 0) {
                    availablePQ.offer(dependent);
                }
            }
        }
        
        // Simulation loop
        while (!availablePQ.isEmpty() || !inProgressPQ.isEmpty()) {
            // Schedule tasks while workers available and tasks are ready
            while (availableWorkers > 0 && !availablePQ.isEmpty()) {
                Task task = availablePQ.poll();
                if (task.executionTime == 0) {
                    // Should not normally occur here, but handle if any exists.
                    task.finishTime = currentTime;
                    for (Task dependent : task.dependents) {
                        dependent.remainingDependencies--;
                        if (dependent.remainingDependencies == 0) {
                            availablePQ.offer(dependent);
                        }
                    }
                    continue;
                }
                // Schedule task on a worker node
                task.startTime = currentTime;
                task.finishTime = currentTime + task.executionTime;
                inProgressPQ.offer(task);
                availableWorkers--;
            }
            
            if (inProgressPQ.isEmpty()) {
                // No tasks in progress; if available remains empty, break simulation.
                if (availablePQ.isEmpty()) {
                    break;
                }
                // Else, advance time minimally (should not happen because available tasks should be ready)
                currentTime++;
                continue;
            }
            
            // Advance time to next task completion
            Task finishedTask = inProgressPQ.poll();
            currentTime = finishedTask.finishTime;
            availableWorkers++;
            // Update dependents of finishedTask
            for (Task dependent : finishedTask.dependents) {
                dependent.remainingDependencies--;
                if (dependent.remainingDependencies == 0) {
                    availablePQ.offer(dependent);
                    // If task is of zero execution time, process it immediately.
                    while (!availablePQ.isEmpty() && availablePQ.peek().executionTime == 0) {
                        Task zeroTask = availablePQ.poll();
                        zeroTask.finishTime = currentTime;
                        for (Task dep : zeroTask.dependents) {
                            dep.remainingDependencies--;
                            if (dep.remainingDependencies == 0) {
                                availablePQ.offer(dep);
                            }
                        }
                    }
                }
            }
        }
        
        // Compute tasks that missed deadlines
        List<Integer> missedDeadlines = new ArrayList<>();
        for (Task task : taskMap.values()) {
            // If finishTime is greater than deadline, mark as missed
            if (task.finishTime > task.deadline) {
                missedDeadlines.add(task.id);
            }
        }
        
        Collections.sort(missedDeadlines);
        return missedDeadlines;
    }
    
    // Cycle detection using Kahn's algorithm.
    private boolean hasCycle(Map<Integer, Task> taskMap, int totalTasks) {
        // Create a copy of in-degrees
        Map<Integer, Integer> inDegree = new HashMap<>();
        Queue<Task> queue = new LinkedList<>();
        for (Task task : taskMap.values()) {
            inDegree.put(task.id, task.remainingDependencies);
            if (task.remainingDependencies == 0) {
                queue.offer(task);
            }
        }
        int processed = 0;
        while (!queue.isEmpty()) {
            Task task = queue.poll();
            processed++;
            for (Task dependent : task.dependents) {
                int deg = inDegree.get(dependent.id) - 1;
                inDegree.put(dependent.id, deg);
                if (deg == 0) {
                    queue.offer(dependent);
                }
            }
        }
        return processed != totalTasks;
    }
    
    // Task class representing each task with its properties.
    private static class Task {
        int id;
        int executionTime;
        int deadline;
        long startTime;
        long finishTime;
        int remainingDependencies;
        List<Task> dependents;
        
        Task(int id, int executionTime, int deadline) {
            this.id = id;
            this.executionTime = executionTime;
            this.deadline = deadline;
            this.remainingDependencies = 0;
            this.dependents = new ArrayList<>();
            this.startTime = -1;
            this.finishTime = -1;
        }
    }
}