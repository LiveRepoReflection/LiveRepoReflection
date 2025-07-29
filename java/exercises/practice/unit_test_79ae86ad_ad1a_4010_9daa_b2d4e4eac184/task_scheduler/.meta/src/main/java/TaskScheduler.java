import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

public class TaskScheduler {
    private final Set<WorkerNode> workerNodes = new HashSet<>();
    private final Map<String, Task> pendingTasks = new ConcurrentHashMap<>();
    private final Map<String, WorkerNode> taskAssignments = new ConcurrentHashMap<>();
    private final PriorityQueue<Task> taskQueue = new PriorityQueue<>(
        Comparator.comparingInt(Task::getPriority)
                  .thenComparing(Task::getDeadline)
    );
    private final Lock lock = new ReentrantLock();
    private final Condition taskAdded = lock.newCondition();

    public void addWorkerNode(WorkerNode node) {
        lock.lock();
        try {
            workerNodes.add(node);
            taskAdded.signalAll();
        } finally {
            lock.unlock();
        }
    }

    public void removeWorkerNode(String nodeId) {
        lock.lock();
        try {
            workerNodes.removeIf(node -> node.getNodeId().equals(nodeId));
            rescheduleAffectedTasks(nodeId);
        } finally {
            lock.unlock();
        }
    }

    public boolean scheduleTask(Task task) {
        lock.lock();
        try {
            if (tryScheduleImmediately(task)) {
                return true;
            }
            pendingTasks.put(task.getTaskId(), task);
            taskQueue.add(task);
            return false;
        } finally {
            lock.unlock();
        }
    }

    public void taskCompleted(String taskId) {
        lock.lock();
        try {
            WorkerNode worker = taskAssignments.remove(taskId);
            if (worker != null) {
                Task task = pendingTasks.remove(taskId);
                if (task != null) {
                    worker.releaseResources(task.getResourceRequirements());
                }
            }
            processPendingTasks();
        } finally {
            lock.unlock();
        }
    }

    public void cancelTask(String taskId) {
        lock.lock();
        try {
            Task task = pendingTasks.remove(taskId);
            if (task != null) {
                taskQueue.remove(task);
                WorkerNode worker = taskAssignments.remove(taskId);
                if (worker != null) {
                    worker.releaseResources(task.getResourceRequirements());
                }
            }
        } finally {
            lock.unlock();
        }
    }

    private boolean tryScheduleImmediately(Task task) {
        if (System.currentTimeMillis() > task.getDeadline()) {
            return false;
        }

        Optional<WorkerNode> suitableWorker = workerNodes.stream()
            .filter(worker -> worker.canAllocateResources(task.getResourceRequirements()))
            .min(Comparator.comparingDouble(this::calculateWorkerUtilization));

        if (suitableWorker.isPresent()) {
            WorkerNode worker = suitableWorker.get();
            worker.allocateResources(task.getResourceRequirements());
            taskAssignments.put(task.getTaskId(), worker);
            pendingTasks.put(task.getTaskId(), task);
            return true;
        }
        return false;
    }

    private void processPendingTasks() {
        lock.lock();
        try {
            while (!taskQueue.isEmpty()) {
                Task task = taskQueue.peek();
                if (tryScheduleImmediately(task)) {
                    taskQueue.poll();
                    pendingTasks.remove(task.getTaskId());
                } else {
                    if (System.currentTimeMillis() > task.getDeadline()) {
                        taskQueue.poll();
                        pendingTasks.remove(task.getTaskId());
                    } else {
                        break;
                    }
                }
            }
        } finally {
            lock.unlock();
        }
    }

    private void rescheduleAffectedTasks(String nodeId) {
        List<Task> affectedTasks = taskAssignments.entrySet().stream()
            .filter(entry -> entry.getValue().getNodeId().equals(nodeId))
            .map(entry -> pendingTasks.get(entry.getKey()))
            .filter(Objects::nonNull)
            .toList();

        affectedTasks.forEach(task -> {
            cancelTask(task.getTaskId());
            scheduleTask(task);
        });
    }

    private double calculateWorkerUtilization(WorkerNode worker) {
        Map<String, Integer> capacity = worker.getResourceCapacity();
        Map<String, Integer> allocation = worker.getCurrentResourceAllocation();

        return allocation.entrySet().stream()
            .mapToDouble(entry -> {
                double total = capacity.getOrDefault(entry.getKey(), 1);
                return entry.getValue() / total;
            })
            .average()
            .orElse(0.0);
    }
}