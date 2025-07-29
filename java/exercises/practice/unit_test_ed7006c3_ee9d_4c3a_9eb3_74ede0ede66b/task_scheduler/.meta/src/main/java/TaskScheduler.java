import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Iterator;

public class TaskScheduler {

    private final Map<String, Worker> workerMap;
    private final Map<String, Task> taskMap;
    private final Map<String, List<Task>> workerTaskAssignment;
    private final PriorityQueue<Task> taskQueue;
    private static final int FAIRNESS_LIMIT = 3;

    public TaskScheduler() {
        workerMap = new HashMap<>();
        taskMap = new HashMap<>();
        workerTaskAssignment = new HashMap<>();
        // Priority queue: higher priority tasks come first; if same, FIFO by submission order (assume insertion order maintained via timestamp)
        taskQueue = new PriorityQueue<>(new Comparator<Task>() {
            public int compare(Task t1, Task t2) {
                int cmp = Integer.compare(t2.getPriority(), t1.getPriority());
                if (cmp == 0) {
                    // Compare submission order using system time
                    return Long.compare(t1.getSubmissionTime(), t2.getSubmissionTime());
                }
                return cmp;
            }
        });
    }

    public synchronized boolean registerWorker(Worker worker) {
        if (worker == null || workerMap.containsKey(worker.getWorkerId())) {
            return false;
        }
        // Set initial heartbeat time
        worker.updateHeartbeat();
        workerMap.put(worker.getWorkerId(), worker);
        workerTaskAssignment.put(worker.getWorkerId(), new ArrayList<>());
        return true;
    }

    public synchronized void workerHeartbeat(String workerId) {
        Worker w = workerMap.get(workerId);
        if (w != null) {
            w.updateHeartbeat();
        }
    }

    public synchronized boolean submitTask(Task task) {
        if (task == null || taskMap.containsKey(task.getTaskId())) {
            // Reject duplicate tasks based on taskId.
            return false;
        }
        task.setState(TaskState.QUEUED);
        task.setSubmissionTime(System.currentTimeMillis());
        taskMap.put(task.getTaskId(), task);
        taskQueue.add(task);
        return true;
    }

    public synchronized void processScheduling() {
        // Clean up failed workers before scheduling in case of heartbeat timeouts.
        removeStaleWorkers();
        
        // Iterate over the task queue; try to schedule each task to one available worker.
        Iterator<Task> iterator = taskQueue.iterator();
        List<Task> scheduledTasks = new ArrayList<>();
        while (iterator.hasNext()) {
            Task task = iterator.next();
            Worker chosenWorker = findWorkerForTask(task);
            if (chosenWorker != null) {
                // Deduct the resources from the worker.
                allocateResources(chosenWorker, task.getResourceRequirements());
                // Update task state.
                task.setState(TaskState.RUNNING);
                // Record assignment.
                workerTaskAssignment.get(chosenWorker.getWorkerId()).add(task);
                scheduledTasks.add(task);
            }
        }
        // Remove scheduled tasks from the queue.
        for (Task t : scheduledTasks) {
            taskQueue.remove(t);
        }
    }
    
    public synchronized List<Task> getTasksForWorker(String workerId) {
        return workerTaskAssignment.getOrDefault(workerId, new ArrayList<>());
    }
    
    public synchronized Task getTaskById(String taskId) {
        return taskMap.get(taskId);
    }
    
    public synchronized void simulateWorkerFailure(String workerId) {
        Worker failedWorker = workerMap.remove(workerId);
        if (failedWorker != null) {
            List<Task> tasksToReschedule = workerTaskAssignment.remove(workerId);
            if (tasksToReschedule != null) {
                // For each task, return resources, mark as QUEUED, and put back into taskQueue.
                for (Task task : tasksToReschedule) {
                    task.setState(TaskState.QUEUED);
                    // No need to add back resources to worker since worker is removed.
                    taskQueue.add(task);
                }
            }
        }
    }
    
    // Helper to choose a suitable worker for a given task.
    private Worker findWorkerForTask(Task task) {
        // For each worker, check if it's alive and has sufficient resources.
        for (Worker worker : workerMap.values()) {
            if (!worker.isAlive()) {
                continue;
            }
            if (!hasSufficientResources(worker.getAvailableResources(), task.getResourceRequirements())) {
                continue;
            }
            // Check fairness: count tasks already assigned to this worker for the same client.
            int clientTaskCount = countClientTasks(worker, task.getClientId());
            if (clientTaskCount >= FAIRNESS_LIMIT) {
                continue;
            }
            // Found a suitable worker.
            return worker;
        }
        return null;
    }
    
    // Helper to allocate resources on the worker
    private void allocateResources(Worker worker, Map<String, Integer> requirements) {
        Map<String, Integer> currentResources = worker.getAvailableResources();
        for (Map.Entry<String, Integer> entry : requirements.entrySet()) {
            String resource = entry.getKey();
            int required = entry.getValue();
            int available = currentResources.getOrDefault(resource, 0);
            currentResources.put(resource, available - required);
        }
    }
    
    // Helper to check if worker's resources satisfy the task requirements.
    private boolean hasSufficientResources(Map<String, Integer> available, Map<String, Integer> required) {
        for (Map.Entry<String, Integer> entry : required.entrySet()) {
            int avail = available.getOrDefault(entry.getKey(), 0);
            if (avail < entry.getValue()) {
                return false;
            }
        }
        return true;
    }
    
    // Helper to count tasks from the same client on the worker.
    private int countClientTasks(Worker worker, String clientId) {
        List<Task> tasks = workerTaskAssignment.get(worker.getWorkerId());
        int count = 0;
        if (tasks != null) {
            for (Task t : tasks) {
                if (t.getClientId().equals(clientId)) {
                    count++;
                }
            }
        }
        return count;
    }
    
    // Remove workers that have not sent a heartbeat in a timely manner.
    private void removeStaleWorkers() {
        List<String> toRemove = new ArrayList<>();
        long currentTime = System.currentTimeMillis();
        for (Worker worker : workerMap.values()) {
            if (!worker.isAlive()) {
                toRemove.add(worker.getWorkerId());
            }
        }
        for (String workerId : toRemove) {
            simulateWorkerFailure(workerId);
        }
    }
}