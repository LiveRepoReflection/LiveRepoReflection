import java.util.*;

public class TaskScheduler {
    /**
     * Finds a schedule that minimizes the total penalty incurred by missed deadlines.
     *
     * @param tasks The list of tasks to schedule
     * @return A list of task IDs representing the optimal schedule
     */
    public List<Integer> findOptimalSchedule(List<Task> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return new ArrayList<>();
        }

        // Build adjacency list for dependency graph
        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        Map<Integer, Task> taskMap = new HashMap<>();

        // Initialize data structures
        for (Task task : tasks) {
            graph.put(task.id, new ArrayList<>());
            inDegree.put(task.id, 0);
            taskMap.put(task.id, task);
        }

        // Build the graph and in-degree counts
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                graph.get(dependency).add(task.id);
                inDegree.put(task.id, inDegree.get(task.id) + 1);
            }
        }

        // Use topological sorting to get all valid orderings
        List<List<Integer>> allValidOrderings = getAllTopologicalOrders(graph, inDegree, tasks.size());
        
        // For large task sets, limit the number of orderings to consider
        if (allValidOrderings.size() > 10000) {
            Collections.shuffle(allValidOrderings);
            allValidOrderings = allValidOrderings.subList(0, 10000);
        }

        // Find ordering with minimum penalty
        List<Integer> bestOrdering = null;
        int minPenalty = Integer.MAX_VALUE;

        for (List<Integer> ordering : allValidOrderings) {
            int penalty = calculatePenalty(ordering, taskMap);
            if (penalty < minPenalty) {
                minPenalty = penalty;
                bestOrdering = ordering;
            }
        }

        // If topological enumeration approach is too slow or the graph is too large,
        // we'll fall back to a heuristic method
        if (bestOrdering == null || tasks.size() > 100) {
            return heuristicSchedule(tasks, graph, inDegree);
        }

        return bestOrdering;
    }

    // For small graphs, enumerate all possible topological orderings
    private List<List<Integer>> getAllTopologicalOrders(Map<Integer, List<Integer>> graph, 
                                                       Map<Integer, Integer> inDegree, 
                                                       int numTasks) {
        List<List<Integer>> result = new ArrayList<>();
        // For large graphs, this would be too expensive - so we limit the size
        if (numTasks > 10) {
            return result; // Will trigger the heuristic method
        }
        
        // Clone in-degree map for use in recursion
        Map<Integer, Integer> inDegreeCopy = new HashMap<>(inDegree);
        List<Integer> current = new ArrayList<>();
        backtrackTopologicalOrders(graph, inDegreeCopy, current, result, numTasks);
        return result;
    }

    private void backtrackTopologicalOrders(Map<Integer, List<Integer>> graph, 
                                           Map<Integer, Integer> inDegree, 
                                           List<Integer> current, 
                                           List<List<Integer>> result, 
                                           int numTasks) {
        // Base case: all tasks scheduled
        if (current.size() == numTasks) {
            result.add(new ArrayList<>(current));
            return;
        }

        // Try each task with 0 in-degree
        for (int taskId : inDegree.keySet()) {
            if (inDegree.get(taskId) == 0) {
                // Add this task to the ordering
                current.add(taskId);
                
                // Mark it as visited by setting in-degree to -1
                inDegree.put(taskId, -1);
                
                // Reduce in-degree of its neighbors
                for (int neighbor : graph.get(taskId)) {
                    inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                }
                
                // Recursively find next tasks
                backtrackTopologicalOrders(graph, inDegree, current, result, numTasks);
                
                // Backtrack
                current.remove(current.size() - 1);
                inDegree.put(taskId, 0);
                for (int neighbor : graph.get(taskId)) {
                    inDegree.put(neighbor, inDegree.get(neighbor) + 1);
                }
            }
        }
    }

    // Calculate total penalty for a given ordering
    private int calculatePenalty(List<Integer> ordering, Map<Integer, Task> taskMap) {
        int currentTime = 0;
        int totalPenalty = 0;
        
        for (int taskId : ordering) {
            Task task = taskMap.get(taskId);
            currentTime += task.duration;
            if (currentTime > task.deadline) {
                totalPenalty += task.penalty;
            }
        }
        
        return totalPenalty;
    }

    // Heuristic approach for large graphs
    private List<Integer> heuristicSchedule(List<Task> tasks, 
                                           Map<Integer, List<Integer>> graph, 
                                           Map<Integer, Integer> inDegree) {
        List<Integer> schedule = new ArrayList<>();
        Map<Integer, Integer> inDegreeCopy = new HashMap<>(inDegree);
        Map<Integer, Task> taskMap = new HashMap<>();
        
        for (Task task : tasks) {
            taskMap.put(task.id, task);
        }
        
        int currentTime = 0;
        
        // Priority queue to determine which task to schedule next
        // We'll try different heuristics for task selection
        while (schedule.size() < tasks.size()) {
            List<Integer> availableTasks = new ArrayList<>();
            
            // Find all tasks with no dependencies left
            for (int taskId : inDegreeCopy.keySet()) {
                if (inDegreeCopy.get(taskId) == 0) {
                    availableTasks.add(taskId);
                }
            }
            
            if (availableTasks.isEmpty()) {
                break; // No tasks available, this shouldn't happen with a valid DAG
            }
            
            // Choose the next task based on several heuristics:
            int nextTaskId = chooseNextTask(availableTasks, taskMap, currentTime);
            
            // Add the selected task to the schedule
            schedule.add(nextTaskId);
            
            // Update the current time
            currentTime += taskMap.get(nextTaskId).duration;
            
            // Mark as scheduled
            inDegreeCopy.put(nextTaskId, -1);
            
            // Update in-degrees of dependent tasks
            for (int neighbor : graph.get(nextTaskId)) {
                if (inDegreeCopy.get(neighbor) > 0) {
                    inDegreeCopy.put(neighbor, inDegreeCopy.get(neighbor) - 1);
                }
            }
        }
        
        return schedule;
    }

    private int chooseNextTask(List<Integer> availableTasks, Map<Integer, Task> taskMap, int currentTime) {
        // Try different heuristics and pick the best one
        
        // Option 1: Earliest Deadline First (EDF)
        int bestTaskEDF = availableTasks.get(0);
        for (int taskId : availableTasks) {
            if (taskMap.get(taskId).deadline < taskMap.get(bestTaskEDF).deadline) {
                bestTaskEDF = taskId;
            }
        }
        
        // Option 2: Least Slack Time (LST)
        int bestTaskLST = availableTasks.get(0);
        for (int taskId : availableTasks) {
            int slackCurrent = taskMap.get(taskId).deadline - (currentTime + taskMap.get(taskId).duration);
            int slackBest = taskMap.get(bestTaskLST).deadline - (currentTime + taskMap.get(bestTaskLST).duration);
            if (slackCurrent < slackBest) {
                bestTaskLST = taskId;
            }
        }
        
        // Option 3: Highest Penalty/Duration Ratio
        int bestTaskPenalty = availableTasks.get(0);
        double bestRatio = (double) taskMap.get(bestTaskPenalty).penalty / taskMap.get(bestTaskPenalty).duration;
        for (int taskId : availableTasks) {
            double ratio = (double) taskMap.get(taskId).penalty / taskMap.get(taskId).duration;
            if (ratio > bestRatio) {
                bestRatio = ratio;
                bestTaskPenalty = taskId;
            }
        }
        
        // Combine heuristics with weights
        // We'll use more weight for tasks that would miss their deadline
        Map<Integer, Double> scores = new HashMap<>();
        for (int taskId : availableTasks) {
            Task task = taskMap.get(taskId);
            double score = 0;
            
            // If task will miss its deadline
            if (currentTime + task.duration > task.deadline) {
                // Prioritize tasks with high penalty and low duration
                score = (double) task.penalty / task.duration * 2;
            } else {
                // For tasks that can meet their deadline, prioritize those with tight deadlines
                int slack = task.deadline - (currentTime + task.duration);
                score = 1000.0 / (slack + 1); // Higher score for smaller slack
            }
            
            scores.put(taskId, score);
        }
        
        // Return task with highest score
        int bestTask = availableTasks.get(0);
        for (int taskId : availableTasks) {
            if (scores.get(taskId) > scores.get(bestTask)) {
                bestTask = taskId;
            }
        }
        
        return bestTask;
    }
}