import java.util.*;

public class TaskScheduler {

    /**
     * Schedules tasks optimally on workers respecting dependencies and deadlines
     * 
     * @param tasks List of tasks to be scheduled
     * @param workers List of workers to execute the tasks
     * @return A list of assignments, or empty list if scheduling is impossible
     */
    public List<Assignment> scheduleTasksOptimally(List<Task> tasks, List<Worker> workers) {
        if (tasks.isEmpty() || workers.isEmpty()) {
            return new ArrayList<>();
        }

        // Check for circular dependencies using topological sort
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.id, task);
        }

        // Create adjacency list representation of the task dependency graph
        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        
        for (Task task : tasks) {
            graph.put(task.id, new ArrayList<>());
            inDegree.put(task.id, 0);
        }
        
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                if (!graph.containsKey(dependency)) {
                    return new ArrayList<>(); // Invalid dependency
                }
                graph.get(dependency).add(task.id);
                inDegree.put(task.id, inDegree.get(task.id) + 1);
            }
        }
        
        // Perform topological sort
        List<Integer> sortedTasks = topologicalSort(graph, inDegree);
        
        // Check for circular dependencies
        if (sortedTasks.size() != tasks.size()) {
            return new ArrayList<>(); // Circular dependency detected
        }
        
        // Apply critical path method to calculate earliest start times
        Map<Integer, Double> earliestStart = calculateEarliestStartTimes(taskMap, graph, sortedTasks);
        
        // Algorithm to assign tasks to workers
        return scheduleTasksWithMinimizedMakespan(taskMap, workers, sortedTasks, earliestStart);
    }
    
    /**
     * Performs a topological sort on the task dependency graph
     */
    private List<Integer> topologicalSort(Map<Integer, List<Integer>> graph, Map<Integer, Integer> inDegree) {
        List<Integer> sorted = new ArrayList<>();
        Queue<Integer> queue = new LinkedList<>();
        
        // Add all nodes with no incoming edges to the queue
        for (Map.Entry<Integer, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.add(entry.getKey());
            }
        }
        
        while (!queue.isEmpty()) {
            int current = queue.poll();
            sorted.add(current);
            
            for (int neighbor : graph.get(current)) {
                inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                if (inDegree.get(neighbor) == 0) {
                    queue.add(neighbor);
                }
            }
        }
        
        return sorted;
    }
    
    /**
     * Calculate the earliest start time for each task using critical path method
     */
    private Map<Integer, Double> calculateEarliestStartTimes(Map<Integer, Task> taskMap, 
                                                             Map<Integer, List<Integer>> graph, 
                                                             List<Integer> sortedTasks) {
        Map<Integer, Double> earliestStart = new HashMap<>();
        
        // Initialize all earliest start times to 0
        for (int taskId : sortedTasks) {
            earliestStart.put(taskId, 0.0);
        }
        
        // Build the reverse graph for finding predecessors
        Map<Integer, List<Integer>> reverseGraph = new HashMap<>();
        for (int taskId : sortedTasks) {
            reverseGraph.put(taskId, new ArrayList<>());
        }
        
        for (Map.Entry<Integer, List<Integer>> entry : graph.entrySet()) {
            int from = entry.getKey();
            for (int to : entry.getValue()) {
                reverseGraph.get(to).add(from);
            }
        }
        
        // Compute earliest start times in topological order
        for (int taskId : sortedTasks) {
            double maxEndTime = 0;
            for (int predecessorId : reverseGraph.get(taskId)) {
                Task predecessor = taskMap.get(predecessorId);
                double predecessorEndTime = earliestStart.get(predecessorId) + predecessor.processing_time;
                maxEndTime = Math.max(maxEndTime, predecessorEndTime);
            }
            earliestStart.put(taskId, maxEndTime);
        }
        
        return earliestStart;
    }
    
    /**
     * Schedule tasks with the goal of minimizing the makespan
     */
    private List<Assignment> scheduleTasksWithMinimizedMakespan(Map<Integer, Task> taskMap, 
                                                               List<Worker> workers, 
                                                               List<Integer> sortedTasks, 
                                                               Map<Integer, Double> earliestStart) {
        // Create PriorityQueue for workers, sorted by earliest available time
        PriorityQueue<WorkerStatus> availableWorkers = new PriorityQueue<>(
            Comparator.comparingDouble(ws -> ws.nextAvailableTime)
        );
        
        for (Worker worker : workers) {
            availableWorkers.add(new WorkerStatus(worker.id, worker.capability, 0.0));
        }
        
        // Create list of assignments
        List<Assignment> assignments = new ArrayList<>();
        
        // Map to track the actual end time of each task
        Map<Integer, Double> actualEndTimes = new HashMap<>();
        
        // Process tasks in topological order
        for (int taskId : sortedTasks) {
            Task task = taskMap.get(taskId);
            
            // Calculate the actual processing time for each worker
            List<Double> processingTimes = new ArrayList<>();
            for (Worker worker : workers) {
                processingTimes.add(task.processing_time / worker.capability);
            }
            
            // Find the best worker for the task
            WorkerStatus bestWorker = null;
            double bestStartTime = Double.MAX_VALUE;
            double bestEndTime = Double.MAX_VALUE;
            
            // Make a copy of the worker queue to restore it after our search
            List<WorkerStatus> workersCopy = new ArrayList<>();
            
            while (!availableWorkers.isEmpty()) {
                WorkerStatus worker = availableWorkers.poll();
                workersCopy.add(worker);
                
                // Calculate the start time for this task on this worker
                double startTime = Math.max(worker.nextAvailableTime, earliestStart.get(taskId));
                double processingTime = task.processing_time / worker.capability;
                double endTime = startTime + processingTime;
                
                // Check if the deadline can be met
                if (endTime <= task.deadline) {
                    // Check if this worker offers a better schedule (earlier end time)
                    if (endTime < bestEndTime) {
                        bestWorker = worker;
                        bestStartTime = startTime;
                        bestEndTime = endTime;
                    }
                }
            }
            
            // Restore the worker queue
            availableWorkers.addAll(workersCopy);
            
            // If we found a suitable worker
            if (bestWorker != null) {
                // Create assignment
                Assignment assignment = new Assignment(taskId, bestWorker.id, bestStartTime, bestEndTime);
                assignments.add(assignment);
                
                // Update worker's next available time
                availableWorkers.remove(bestWorker);
                bestWorker.nextAvailableTime = bestEndTime;
                availableWorkers.add(bestWorker);
                
                // Record the actual end time of this task
                actualEndTimes.put(taskId, bestEndTime);
            } else {
                // Could not schedule this task, return empty list
                return new ArrayList<>();
            }
        }
        
        // Final check to ensure dependencies are respected
        for (int taskId : sortedTasks) {
            Task task = taskMap.get(taskId);
            for (int depId : task.dependencies) {
                Assignment taskAssignment = null;
                Assignment depAssignment = null;
                
                for (Assignment a : assignments) {
                    if (a.taskId == taskId) taskAssignment = a;
                    if (a.taskId == depId) depAssignment = a;
                }
                
                if (taskAssignment != null && depAssignment != null) {
                    if (depAssignment.endTime > taskAssignment.startTime) {
                        return new ArrayList<>(); // Dependency constraint violated
                    }
                }
            }
        }
        
        return assignments;
    }
    
    /**
     * Helper class to track worker status
     */
    private static class WorkerStatus {
        int id;
        double capability;
        double nextAvailableTime;
        
        public WorkerStatus(int id, double capability, double nextAvailableTime) {
            this.id = id;
            this.capability = capability;
            this.nextAvailableTime = nextAvailableTime;
        }
    }
}