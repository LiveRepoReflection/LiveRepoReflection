import java.util.*;
import java.util.stream.Collectors;

public class TaskScheduler {
    public Map<String, String> schedule(List<Task> tasks, List<Machine> machines, int[][] networkCost) {
        Map<String, String> schedule = new HashMap<>();
        if (tasks.isEmpty() || machines.isEmpty()) return schedule;

        // Create a priority queue of tasks sorted by priority (highest first)
        PriorityQueue<Task> taskQueue = new PriorityQueue<>((t1, t2) -> t2.getPriority() - t1.getPriority());
        
        // Keep track of remaining resources on each machine
        Map<String, Map<String, Integer>> remainingResources = new HashMap<>();
        for (Machine machine : machines) {
            remainingResources.put(machine.getMachineId(), 
                new HashMap<>(machine.getAvailableResources()));
        }

        // Keep track of completed tasks for dependency resolution
        Set<String> completedTasks = new HashSet<>();
        
        // First, add tasks with no dependencies to the queue
        List<Task> tasksWithNoDependencies = tasks.stream()
            .filter(task -> task.getDependencies().isEmpty())
            .collect(Collectors.toList());
        taskQueue.addAll(tasksWithNoDependencies);

        // Process tasks until queue is empty or no more tasks can be scheduled
        while (!taskQueue.isEmpty()) {
            Task currentTask = taskQueue.poll();
            String bestMachine = findBestMachine(currentTask, machines, remainingResources, networkCost);
            
            if (bestMachine != null) {
                // Schedule the task
                schedule.put(currentTask.getTaskId(), bestMachine);
                completedTasks.add(currentTask.getTaskId());
                
                // Update remaining resources
                updateResources(remainingResources.get(bestMachine), 
                             currentTask.getResourceRequirements());

                // Check for newly eligible tasks (whose dependencies are now met)
                addNewlyEligibleTasks(tasks, taskQueue, completedTasks);
            }
        }
        
        return schedule;
    }

    private String findBestMachine(Task task, List<Machine> machines,
                                 Map<String, Map<String, Integer>> remainingResources,
                                 int[][] networkCost) {
        String bestMachine = null;
        int lowestCost = Integer.MAX_VALUE;

        for (int i = 0; i < machines.size(); i++) {
            Machine machine = machines.get(i);
            if (canScheduleOnMachine(task, remainingResources.get(machine.getMachineId()))) {
                // Calculate total cost including network transfer
                int totalCost = calculateTotalCost(task, machine, i, networkCost);
                if (totalCost < lowestCost) {
                    lowestCost = totalCost;
                    bestMachine = machine.getMachineId();
                }
            }
        }

        return bestMachine;
    }

    private boolean canScheduleOnMachine(Task task, Map<String, Integer> remainingResources) {
        for (Map.Entry<String, Integer> requirement : task.getResourceRequirements().entrySet()) {
            String resourceType = requirement.getKey();
            int requiredAmount = requirement.getValue();
            
            if (!remainingResources.containsKey(resourceType) ||
                remainingResources.get(resourceType) < requiredAmount) {
                return false;
            }
        }
        return true;
    }

    private void updateResources(Map<String, Integer> remainingResources, 
                               Map<String, Integer> requirements) {
        for (Map.Entry<String, Integer> requirement : requirements.entrySet()) {
            String resourceType = requirement.getKey();
            int requiredAmount = requirement.getValue();
            remainingResources.put(resourceType, 
                remainingResources.get(resourceType) - requiredAmount);
        }
    }

    private int calculateTotalCost(Task task, Machine machine, int machineIndex, 
                                 int[][] networkCost) {
        // Base cost is the network transfer cost
        int cost = 0;
        
        // Add network transfer costs
        for (int i = 0; i < networkCost.length; i++) {
            if (i != machineIndex) {
                cost += networkCost[i][machineIndex] * task.getDataSize();
            }
        }

        // Add waiting cost based on priority
        cost += task.getPriority();

        return cost;
    }

    private void addNewlyEligibleTasks(List<Task> allTasks, Queue<Task> taskQueue, 
                                     Set<String> completedTasks) {
        for (Task task : allTasks) {
            if (!completedTasks.contains(task.getTaskId()) && 
                !taskQueue.contains(task) &&
                completedTasks.containsAll(task.getDependencies())) {
                taskQueue.add(task);
            }
        }
    }
}