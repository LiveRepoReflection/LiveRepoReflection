import java.util.*;
import java.util.stream.Collectors;

public class TaskScheduler {
    private final Map<Integer, Task> tasks;
    private final Map<Integer, Worker> workers;
    private int taskIdCounter;
    private int workerIdCounter;

    public TaskScheduler() {
        tasks = new HashMap<>();
        workers = new HashMap<>();
        taskIdCounter = 1;
        workerIdCounter = 1;
    }

    public synchronized int addTask(Set<String> requiredResources, List<Integer> dependencies, int estimatedTime, int priority) {
        // Create a new task with a unique id
        int id = taskIdCounter++;
        Task task = new Task(id, requiredResources, new ArrayList<>(dependencies), estimatedTime, priority);
        tasks.put(id, task);
        return id;
    }

    public synchronized void removeTask(int taskId) {
        if (!tasks.containsKey(taskId)) {
            throw new IllegalArgumentException("Task with id " + taskId + " does not exist.");
        }
        // If the task is assigned to a worker, free that worker
        Task task = tasks.get(taskId);
        if (task.assignedWorker != -1) {
            Worker wk = workers.get(task.assignedWorker);
            if (wk != null) {
                wk.currentTask = -1;
            }
        }
        tasks.remove(taskId);
    }

    public synchronized int addWorker(Set<String> availableResources) {
        int id = workerIdCounter++;
        Worker worker = new Worker(id, availableResources);
        workers.put(id, worker);
        return id;
    }

    public synchronized void removeWorker(int workerId) {
        if (!workers.containsKey(workerId)) {
            throw new IllegalArgumentException("Worker with id " + workerId + " does not exist.");
        }
        // If worker is assigned a task, leave that assignment undefined as per requirement.
        workers.remove(workerId);
    }

    public synchronized void assignTasks() {
        // Create a list of idle workers sorted by ascending available resources size.
        List<Worker> idleWorkers = workers.values().stream()
                .filter(worker -> worker.currentTask == -1)
                .sorted(Comparator.comparingInt(w -> w.availableResources.size()))
                .collect(Collectors.toList());

        // For each idle worker, assign the best candidate task if available.
        for (Worker worker : idleWorkers) {
            // Build a list of candidate tasks:
            List<Task> candidateTasks = tasks.values().stream()
                    .filter(task -> !task.completed)
                    .filter(task -> task.assignedWorker == -1)
                    .filter(task -> getTaskStatus(task.id).equals("Ready"))
                    .filter(task -> worker.hasResources(task.requiredResources))
                    .collect(Collectors.toList());
            if (candidateTasks.isEmpty())
                continue;
            // Select the candidate with highest priority; if tie, choose the one with smallest id.
            Task selectedTask = candidateTasks.stream().max(Comparator.comparingInt(Task::getPriority)
                    .thenComparingInt(task -> -task.id)).orElse(null);
            if (selectedTask != null) {
                // Assign task to worker
                selectedTask.assignedWorker = worker.id;
                worker.currentTask = selectedTask.id;
            }
        }
    }

    public synchronized void markTaskCompleted(int taskId) {
        if (!tasks.containsKey(taskId))
            throw new IllegalArgumentException("Task with id " + taskId + " does not exist.");
        Task task = tasks.get(taskId);
        task.completed = true;
        // Free the worker if task was assigned.
        if (task.assignedWorker != -1) {
            Worker worker = workers.get(task.assignedWorker);
            if (worker != null) {
                worker.currentTask = -1;
            }
            // Mark task as no longer assigned.
            task.assignedWorker = -1;
        }
    }

    public synchronized Map<Integer, Integer> getWorkerTaskAssignments() {
        // Return a map of workerId -> taskId for workers currently running a task.
        Map<Integer, Integer> assignments = new HashMap<>();
        for (Worker worker : workers.values()) {
            if (worker.currentTask != -1) {
                assignments.put(worker.id, worker.currentTask);
            }
        }
        return assignments;
    }

    public synchronized String getTaskStatus(int taskId) {
        if (!tasks.containsKey(taskId))
            throw new IllegalArgumentException("Task with id " + taskId + " does not exist.");
        Task task = tasks.get(taskId);
        if (task.completed)
            return "Completed";
        if (task.assignedWorker != -1)
            return "Running";
        // Check dependencies: if any dependency is not completed, then task is blocked.
        for (Integer depId : task.dependencies) {
            Task depTask = tasks.get(depId);
            if (depTask == null || !depTask.completed) {
                return "Blocked";
            }
        }
        return "Ready";
    }

    // Inner class representing a Task.
    private static class Task {
        private final int id;
        private final Set<String> requiredResources;
        private final List<Integer> dependencies;
        private final int estimatedTime;
        private final int priority;
        private boolean completed;
        private int assignedWorker;

        public Task(int id, Set<String> requiredResources, List<Integer> dependencies, int estimatedTime, int priority) {
            this.id = id;
            this.requiredResources = new HashSet<>(requiredResources);
            this.dependencies = new ArrayList<>(dependencies);
            this.estimatedTime = estimatedTime;
            this.priority = priority;
            this.completed = false;
            this.assignedWorker = -1;
        }

        public int getPriority() {
            return priority;
        }
    }

    // Inner class representing a Worker.
    private static class Worker {
        private final int id;
        private final Set<String> availableResources;
        private int currentTask;

        public Worker(int id, Set<String> availableResources) {
            this.id = id;
            this.availableResources = new HashSet<>(availableResources);
            this.currentTask = -1;
        }

        public boolean hasResources(Set<String> required) {
            return availableResources.containsAll(required);
        }
    }
}