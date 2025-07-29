package task_scheduler;

import java.util.*;

public class TaskScheduler {

    private static class RunningTask {
        int taskId;
        int finishTime;
        
        RunningTask(int taskId, int finishTime) {
            this.taskId = taskId;
            this.finishTime = finishTime;
        }
    }
    
    public int schedule(int n, int[][] dependencies, int resources, int[] taskResources, int[] taskExecutionTimes) {
        // Build graph and in-degree count.
        List<List<Integer>> graph = new ArrayList<>();
        int[] inDegree = new int[n];
        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        
        for (int[] dep : dependencies) {
            int from = dep[0];
            int to = dep[1];
            graph.get(from).add(to);
            inDegree[to]++;
        }
        
        // Initialize ready queue: tasks with inDegree 0.
        // Use a priority queue based on resource requirement (ascending) and then task id.
        PriorityQueue<Integer> ready = new PriorityQueue<>(
            (a, b) -> {
                if (taskResources[a] != taskResources[b])
                    return taskResources[a] - taskResources[b];
                return a - b;
            }
        );
        
        for (int i = 0; i < n; i++) {
            if (inDegree[i] == 0) {
                ready.offer(i);
            }
        }
        
        // PriorityQueue for running tasks (ordered by finish time).
        PriorityQueue<RunningTask> running = new PriorityQueue<>(
            Comparator.comparingInt(rt -> rt.finishTime)
        );
        
        int currentTime = 0;
        int availableResource = resources;
        int finishedTasks = 0;
        
        // Simulation loop until all tasks are finished.
        while (finishedTasks < n) {
            boolean scheduledTask = false;
            // Try to schedule tasks from ready queue if resources permit.
            // Since tasks in ready are sorted by resource requirement,
            // iterate over a temporary list to try to schedule them.
            List<Integer> toRequeue = new ArrayList<>();
            while (!ready.isEmpty()) {
                int task = ready.poll();
                if (taskResources[task] <= availableResource) {
                    // Schedule this task immediately.
                    availableResource -= taskResources[task];
                    int finishTime = currentTime + taskExecutionTimes[task];
                    running.offer(new RunningTask(task, finishTime));
                    scheduledTask = true;
                } else {
                    // Cannot schedule now, try later.
                    toRequeue.add(task);
                }
            }
            // Re-add tasks that couldn't be scheduled.
            for (int task : toRequeue) {
                ready.offer(task);
            }
            
            if (!scheduledTask) {
                // If no tasks scheduled, advance time to the next finish event.
                if (running.isEmpty()) {
                    // There might be tasks waiting due to resource constraints.
                    // This condition should not occur because tasks that cannot be scheduled
                    // will eventually free resources when running tasks complete.
                    break;
                }
                
                RunningTask nextFinished = running.peek();
                currentTime = nextFinished.finishTime;
                // Process all tasks finishing at currentTime.
                while (!running.isEmpty() && running.peek().finishTime == currentTime) {
                    RunningTask finishedTask = running.poll();
                    finishedTasks++;
                    availableResource += taskResources[finishedTask.taskId];
                    // For each dependent task, reduce in-degree.
                    for (int neighbor : graph.get(finishedTask.taskId)) {
                        inDegree[neighbor]--;
                        if (inDegree[neighbor] == 0) {
                            ready.offer(neighbor);
                        }
                    }
                }
            }
        }
        
        return currentTime;
    }
    
    // Main method for ad-hoc testing if needed.
    public static void main(String[] args) {
        // Example usage
        int n = 4;
        int[][] dependencies = { {0, 1}, {0, 2}, {1, 3}, {2, 3} };
        int resources = 10;
        int[] taskResources = {3, 4, 2, 5};
        int[] taskExecutionTimes = {2, 3, 1, 4};
        
        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        System.out.println("Makespan: " + makespan);
    }
}