import java.util.*;

public class TaskScheduler {
    
    /**
     * Schedules tasks optimally to maximize the number completed before their deadlines.
     * 
     * @param tasks List of tasks to be scheduled
     * @param systemResources Available system resources
     * @return Ordered list of task IDs representing the optimal execution schedule
     */
    public List<String> schedule(List<Task> tasks, Map<String, Integer> systemResources) {
        if (tasks.isEmpty()) {
            return new ArrayList<>();
        }
        
        // Create a graph representation for dependency checking
        Map<String, Set<String>> dependencyGraph = buildDependencyGraph(tasks);
        Map<String, Task> taskMap = createTaskMap(tasks);
        
        // Check for circular dependencies
        if (hasCircularDependencies(dependencyGraph, taskMap)) {
            return new ArrayList<>();
        }
        
        // This will track the completion time for each task
        Map<String, Integer> completionTimes = new HashMap<>();
        
        // Keep track of available resources at each point in time
        Map<String, Integer> availableResources = new HashMap<>(systemResources);
        
        // Keeps track of tasks that have been scheduled
        Set<String> scheduledTasks = new HashSet<>();
        
        // The resulting schedule
        List<String> schedule = new ArrayList<>();
        
        // Current time in the simulation
        int currentTime = 0;
        
        // Loop until all tasks are scheduled or no more tasks can be scheduled
        while (scheduledTasks.size() < tasks.size()) {
            List<Task> eligibleTasks = new ArrayList<>();
            
            // Find all eligible tasks at the current time
            for (Task task : tasks) {
                if (!scheduledTasks.contains(task.getId()) && 
                    areAllDependenciesMet(task, scheduledTasks) && 
                    enoughResourcesAvailable(task, availableResources)) {
                    
                    // Check if the task can finish before its deadline
                    if (currentTime + task.getExecutionTime() <= task.getDeadline()) {
                        eligibleTasks.add(task);
                    }
                }
            }
            
            if (eligibleTasks.isEmpty()) {
                // If no eligible tasks, try to advance time to next possible task
                boolean advanced = advanceTimeToNextEligibleTask(
                    currentTime, tasks, scheduledTasks, completionTimes, 
                    availableResources, systemResources);
                
                if (!advanced) {
                    // No tasks can be scheduled anymore
                    break;
                }
            } else {
                // Select the best task based on priority heuristic
                Task selectedTask = selectBestTask(eligibleTasks);
                
                // Schedule the selected task
                schedule.add(selectedTask.getId());
                scheduledTasks.add(selectedTask.getId());
                
                // Update resources
                allocateResources(selectedTask, availableResources);
                
                // Update time and completion time for this task
                int taskCompletionTime = currentTime + selectedTask.getExecutionTime();
                completionTimes.put(selectedTask.getId(), taskCompletionTime);
                currentTime = taskCompletionTime;
                
                // Release resources for completed tasks
                releaseResources(currentTime, completionTimes, taskMap, availableResources);
            }
        }
        
        // Final verification - ensure the schedule is valid
        if (!isValidSchedule(schedule, taskMap, systemResources)) {
            return new ArrayList<>();
        }
        
        return schedule;
    }
    
    /**
     * Builds a graph representation of task dependencies.
     */
    private Map<String, Set<String>> buildDependencyGraph(List<Task> tasks) {
        Map<String, Set<String>> graph = new HashMap<>();
        
        for (Task task : tasks) {
            graph.put(task.getId(), new HashSet<>());
        }
        
        for (Task task : tasks) {
            for (String dependency : task.getDependencies()) {
                graph.get(dependency).add(task.getId());
            }
        }
        
        return graph;
    }
    
    /**
     * Creates a map of task IDs to Task objects for quick lookup.
     */
    private Map<String, Task> createTaskMap(List<Task> tasks) {
        Map<String, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.getId(), task);
        }
        return taskMap;
    }
    
    /**
     * Checks if the dependency graph has circular dependencies using DFS.
     */
    private boolean hasCircularDependencies(Map<String, Set<String>> graph, Map<String, Task> taskMap) {
        Set<String> visited = new HashSet<>();
        Set<String> recursionStack = new HashSet<>();
        
        for (String taskId : graph.keySet()) {
            if (isCircular(taskId, graph, visited, recursionStack, taskMap)) {
                return true;
            }
        }
        
        return false;
    }
    
    /**
     * Helper method for detecting cycles in the dependency graph.
     */
    private boolean isCircular(String taskId, Map<String, Set<String>> graph, 
                              Set<String> visited, Set<String> recursionStack,
                              Map<String, Task> taskMap) {
        if (recursionStack.contains(taskId)) {
            return true;
        }
        
        if (visited.contains(taskId)) {
            return false;
        }
        
        visited.add(taskId);
        recursionStack.add(taskId);
        
        // Check all dependencies of the current task
        for (String dependency : taskMap.get(taskId).getDependencies()) {
            if (graph.containsKey(dependency) && 
                isCircular(dependency, graph, visited, recursionStack, taskMap)) {
                return true;
            }
        }
        
        recursionStack.remove(taskId);
        return false;
    }
    
    /**
     * Checks if all dependencies of a task have been scheduled.
     */
    private boolean areAllDependenciesMet(Task task, Set<String> scheduledTasks) {
        for (String dependency : task.getDependencies()) {
            if (!scheduledTasks.contains(dependency)) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Checks if enough resources are available to execute a task.
     */
    private boolean enoughResourcesAvailable(Task task, Map<String, Integer> availableResources) {
        for (Map.Entry<String, Integer> entry : task.getResourceRequirements().entrySet()) {
            String resourceType = entry.getKey();
            int requiredAmount = entry.getValue();
            
            if (!availableResources.containsKey(resourceType) || 
                availableResources.get(resourceType) < requiredAmount) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Allocates resources for a task execution.
     */
    private void allocateResources(Task task, Map<String, Integer> availableResources) {
        for (Map.Entry<String, Integer> entry : task.getResourceRequirements().entrySet()) {
            String resourceType = entry.getKey();
            int requiredAmount = entry.getValue();
            
            availableResources.put(resourceType, availableResources.get(resourceType) - requiredAmount);
        }
    }
    
    /**
     * Releases resources from completed tasks.
     */
    private void releaseResources(int currentTime, Map<String, Integer> completionTimes, 
                                 Map<String, Task> taskMap, Map<String, Integer> availableResources) {
        for (Map.Entry<String, Integer> entry : completionTimes.entrySet()) {
            String taskId = entry.getKey();
            int completionTime = entry.getValue();
            
            if (completionTime <= currentTime) {
                Task task = taskMap.get(taskId);
                
                for (Map.Entry<String, Integer> resourceEntry : task.getResourceRequirements().entrySet()) {
                    String resourceType = resourceEntry.getKey();
                    int amount = resourceEntry.getValue();
                    
                    availableResources.put(resourceType, availableResources.get(resourceType) + amount);
                }
                
                // Remove the task from completionTimes to avoid releasing resources multiple times
                completionTimes.remove(taskId);
                return; // We only release one task's resources at a time to avoid concurrent modification
            }
        }
    }
    
    /**
     * Selects the best task to execute next based on a priority heuristic.
     * 
     * Current implementation uses Earliest Deadline First with tie-breaking
     * on shortest execution time and then lexicographically by ID.
     */
    private Task selectBestTask(List<Task> eligibleTasks) {
        return Collections.min(eligibleTasks, (t1, t2) -> {
            // Priority 1: Earliest deadline first
            int deadlineComparison = Integer.compare(t1.getDeadline(), t2.getDeadline());
            if (deadlineComparison != 0) {
                return deadlineComparison;
            }
            
            // Priority 2: Shortest execution time
            int executionTimeComparison = Integer.compare(t1.getExecutionTime(), t2.getExecutionTime());
            if (executionTimeComparison != 0) {
                return executionTimeComparison;
            }
            
            // Priority 3: Lexicographical ordering of task IDs
            return t1.getId().compareTo(t2.getId());
        });
    }
    
    /**
     * Advances time to the next point where a task might become eligible.
     * This happens when resources are released after a task completes.
     */
    private boolean advanceTimeToNextEligibleTask(int currentTime, List<Task> tasks, 
                                                Set<String> scheduledTasks, 
                                                Map<String, Integer> completionTimes,
                                                Map<String, Integer> availableResources,
                                                Map<String, Integer> systemResources) {
        // Find the next time when resources will be released
        int nextReleaseTime = Integer.MAX_VALUE;
        for (int completionTime : completionTimes.values()) {
            if (completionTime > currentTime && completionTime < nextReleaseTime) {
                nextReleaseTime = completionTime;
            }
        }
        
        if (nextReleaseTime != Integer.MAX_VALUE) {
            // Advance time to the next release time
            int oldTime = currentTime;
            currentTime = nextReleaseTime;
            
            // Reset available resources to system resources
            for (Map.Entry<String, Integer> entry : systemResources.entrySet()) {
                availableResources.put(entry.getKey(), entry.getValue());
            }
            
            // Re-allocate resources for tasks that are still executing
            for (Map.Entry<String, Integer> entry : completionTimes.entrySet()) {
                String taskId = entry.getKey();
                int taskCompletionTime = entry.getValue();
                
                if (taskCompletionTime > currentTime) {
                    Task task = null;
                    for (Task t : tasks) {
                        if (t.getId().equals(taskId)) {
                            task = t;
                            break;
                        }
                    }
                    
                    if (task != null) {
                        allocateResources(task, availableResources);
                    }
                }
            }
            
            // Release resources for completed tasks
            releaseResources(currentTime, completionTimes, createTaskMap(tasks), availableResources);
            
            return true;
        }
        
        return false;
    }
    
    /**
     * Validates that the final schedule meets all constraints.
     */
    private boolean isValidSchedule(List<String> schedule, Map<String, Task> taskMap, 
                                   Map<String, Integer> systemResources) {
        if (schedule.isEmpty()) {
            return true;
        }
        
        Set<String> scheduledTasks = new HashSet<>();
        Map<String, Integer> availableResources = new HashMap<>(systemResources);
        int currentTime = 0;
        
        for (String taskId : schedule) {
            Task task = taskMap.get(taskId);
            
            // Check dependencies
            for (String dependency : task.getDependencies()) {
                if (!scheduledTasks.contains(dependency)) {
                    return false;
                }
            }
            
            // Check resources
            for (Map.Entry<String, Integer> entry : task.getResourceRequirements().entrySet()) {
                String resourceType = entry.getKey();
                int requiredAmount = entry.getValue();
                
                if (!availableResources.containsKey(resourceType) || 
                    availableResources.get(resourceType) < requiredAmount) {
                    return false;
                }
                
                // Allocate resources
                availableResources.put(resourceType, availableResources.get(resourceType) - requiredAmount);
            }
            
            // Update time
            currentTime += task.getExecutionTime();
            
            // Check deadline
            if (currentTime > task.getDeadline()) {
                return false;
            }
            
            // Add to scheduled tasks
            scheduledTasks.add(taskId);
            
            // Release resources (simplified for validation)
            for (Map.Entry<String, Integer> entry : task.getResourceRequirements().entrySet()) {
                String resourceType = entry.getKey();
                int requiredAmount = entry.getValue();
                
                availableResources.put(resourceType, availableResources.get(resourceType) + requiredAmount);
            }
        }
        
        return true;
    }
}