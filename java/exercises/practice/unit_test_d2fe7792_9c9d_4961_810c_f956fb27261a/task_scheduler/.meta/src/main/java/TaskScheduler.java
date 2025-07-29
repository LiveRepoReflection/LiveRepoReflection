import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

public class TaskScheduler {
    private Map<String, Task> tasks;
    private Map<String, WorkerNode> workers;
    private List<String> executionLog;
    private int maxRetries;
    private AtomicLong submissionCounter;

    public TaskScheduler(int maxRetries) {
        this.maxRetries = maxRetries;
        this.tasks = new HashMap<>();
        this.workers = new HashMap<>();
        this.executionLog = new ArrayList<>();
        this.submissionCounter = new AtomicLong(0);
    }

    public synchronized void registerWorker(WorkerNode worker) {
        workers.put(worker.getWorkerId(), worker);
    }

    public synchronized void submitTask(Task task) {
        task.setSubmissionTime(submissionCounter.incrementAndGet());
        tasks.put(task.getTaskId(), task);
        if (detectCycle()) {
            tasks.remove(task.getTaskId());
            throw new IllegalArgumentException("Circular dependency detected");
        }
    }

    private boolean detectCycle() {
        Map<String, Boolean> visited = new HashMap<>();
        Map<String, Boolean> recStack = new HashMap<>();
        for (String taskId : tasks.keySet()) {
            visited.put(taskId, false);
            recStack.put(taskId, false);
        }
        for (String taskId : tasks.keySet()) {
            if (isCyclicUtil(taskId, visited, recStack)) {
                return true;
            }
        }
        return false;
    }

    private boolean isCyclicUtil(String taskId, Map<String, Boolean> visited, Map<String, Boolean> recStack) {
        if (!visited.get(taskId)) {
            visited.put(taskId, true);
            recStack.put(taskId, true);
            Task task = tasks.get(taskId);
            for (String depId : task.getDependencies()) {
                if (tasks.containsKey(depId)) {
                    if (!visited.get(depId) && isCyclicUtil(depId, visited, recStack))
                        return true;
                    else if (recStack.get(depId))
                        return true;
                }
            }
        }
        recStack.put(taskId, false);
        return false;
    }

    public void executeAll() {
        boolean progress;
        do {
            progress = false;
            List<Task> taskList;
            synchronized(this) {
                taskList = new ArrayList<>();
                for (Task t : tasks.values()) {
                    if (t.getStatus() == TaskStatus.PENDING && dependenciesCompleted(t)) {
                        taskList.add(t);
                    }
                }
                Collections.sort(taskList);
            }
            for (Task task : taskList) {
                WorkerNode assignedWorker = findWorkerForTask(task);
                if (assignedWorker != null) {
                    progress = true;
                    executeTask(task, assignedWorker);
                }
            }
            try {
                Thread.sleep(10);
            } catch(InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        } while (progress);
    }

    private boolean dependenciesCompleted(Task task) {
        for (String dep : task.getDependencies()) {
            Task depTask = tasks.get(dep);
            if (depTask == null || depTask.getStatus() != TaskStatus.COMPLETED) {
                return false;
            }
        }
        return true;
    }

    private WorkerNode findWorkerForTask(Task task) {
        synchronized(this) {
            for (WorkerNode worker : workers.values()) {
                synchronized(worker) {
                    if (worker.isActive() && worker.canAllocate(task.getRequiredResource())) {
                        return worker;
                    }
                }
            }
        }
        return null;
    }

    private void executeTask(Task task, WorkerNode worker) {
        synchronized(this) {
            if (task.getStatus() != TaskStatus.PENDING) {
                return;
            }
            synchronized(worker) {
                if (!worker.isActive() || !worker.canAllocate(task.getRequiredResource())) {
                    return;
                }
                worker.allocate(task.getRequiredResource());
                task.setStatus(TaskStatus.RUNNING);
                task.setAssignedWorker(worker.getWorkerId());
            }
        }
        try {
            Thread.sleep(50);
            synchronized(this) {
                WorkerNode currentWorker = workers.get(task.getAssignedWorker());
                if (currentWorker == null || !currentWorker.isActive()) {
                    throw new Exception("Worker failure");
                }
                task.setStatus(TaskStatus.COMPLETED);
                executionLog.add(task.getTaskId());
            }
        } catch(Exception e) {
            synchronized(this) {
                task.setStatus(TaskStatus.FAILED);
                task.incrementRetryCount();
            }
        } finally {
            WorkerNode currentWorker;
            synchronized(this) {
                currentWorker = workers.get(task.getAssignedWorker());
            }
            if (currentWorker != null) {
                synchronized(currentWorker) {
                    currentWorker.release(task.getRequiredResource());
                }
            }
            synchronized(this) {
                if (task.getStatus() == TaskStatus.FAILED && task.getRetryCount() <= maxRetries) {
                    task.setStatus(TaskStatus.PENDING);
                    task.setAssignedWorker(null);
                }
            }
        }
    }

    public synchronized TaskStatus getTaskStatus(String taskId) {
        Task task = tasks.get(taskId);
        if (task != null) {
            return task.getStatus();
        }
        return null;
    }

    public synchronized java.util.List<String> getExecutionLog() {
        return new ArrayList<>(executionLog);
    }

    public synchronized String getTaskAssignedWorker(String taskId) {
        Task task = tasks.get(taskId);
        if (task != null) {
            return task.getAssignedWorker();
        }
        return null;
    }

    public void simulateWorkerFailure(String workerId) {
        WorkerNode worker;
        synchronized(this) {
            worker = workers.get(workerId);
            if (worker != null) {
                worker.deactivate();
                for (Task task : tasks.values()) {
                    if (workerId.equals(task.getAssignedWorker()) && task.getStatus() == TaskStatus.RUNNING) {
                        task.setStatus(TaskStatus.FAILED);
                        task.incrementRetryCount();
                        task.setAssignedWorker(null);
                    }
                }
            }
        }
    }
}