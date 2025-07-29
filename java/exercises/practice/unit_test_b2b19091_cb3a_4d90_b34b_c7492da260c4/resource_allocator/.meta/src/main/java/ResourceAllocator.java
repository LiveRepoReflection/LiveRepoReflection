import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Comparator;
import java.util.concurrent.ConcurrentHashMap;

public class ResourceAllocator {
    private final Map<String, Integer> availableResources;
    private final Map<String, Task> activeTasks;
    private final PriorityQueue<Task> pendingTasks;
    private final long allocationTimeout;

    public ResourceAllocator(Map<String, Integer> initialResources) {
        this(initialResources, 100);
    }

    public ResourceAllocator(Map<String, Integer> initialResources, long allocationTimeoutMs) {
        this.availableResources = new ConcurrentHashMap<>(initialResources);
        this.activeTasks = new ConcurrentHashMap<>();
        this.pendingTasks = new PriorityQueue<>(Comparator.comparingInt(Task::getPriority).reversed());
        this.allocationTimeout = allocationTimeoutMs;
    }

    public synchronized boolean allocateResources(String taskId, int priority, 
            Map<String, Integer> requirements, long arrivalTime, long deadline, long executionTime) {
        long startTime = System.currentTimeMillis();
        
        if (System.currentTimeMillis() > deadline) {
            return false;
        }

        if (canAllocate(requirements)) {
            allocateTask(taskId, priority, requirements, arrivalTime, deadline, executionTime);
            return true;
        }

        if (tryPreemptLowerPriorityTasks(priority, requirements)) {
            allocateTask(taskId, priority, requirements, arrivalTime, deadline, executionTime);
            return true;
        }

        if (System.currentTimeMillis() - startTime > allocationTimeout) {
            return false;
        }

        pendingTasks.add(new Task(taskId, priority, requirements, arrivalTime, deadline, executionTime));
        return false;
    }

    private boolean canAllocate(Map<String, Integer> requirements) {
        for (Map.Entry<String, Integer> entry : requirements.entrySet()) {
            String resource = entry.getKey();
            int required = entry.getValue();
            int available = availableResources.getOrDefault(resource, 0);
            if (required > available) {
                return false;
            }
        }
        return true;
    }

    private void allocateTask(String taskId, int priority, Map<String, Integer> requirements, 
            long arrivalTime, long deadline, long executionTime) {
        for (Map.Entry<String, Integer> entry : requirements.entrySet()) {
            String resource = entry.getKey();
            int required = entry.getValue();
            availableResources.compute(resource, (k, v) -> v - required);
        }

        Task task = new Task(taskId, priority, requirements, arrivalTime, deadline, executionTime);
        activeTasks.put(taskId, task);
    }

    private boolean tryPreemptLowerPriorityTasks(int newPriority, Map<String, Integer> newRequirements) {
        for (Task task : activeTasks.values()) {
            if (task.getPriority() < newPriority && canAllocateAfterPreemption(task, newRequirements)) {
                preemptTask(task);
                return true;
            }
        }
        return false;
    }

    private boolean canAllocateAfterPreemption(Task taskToPreempt, Map<String, Integer> newRequirements) {
        Map<String, Integer> tempResources = new HashMap<>(availableResources);
        for (Map.Entry<String, Integer> entry : taskToPreempt.getRequirements().entrySet()) {
            String resource = entry.getKey();
            int released = entry.getValue();
            tempResources.merge(resource, released, Integer::sum);
        }

        for (Map.Entry<String, Integer> entry : newRequirements.entrySet()) {
            String resource = entry.getKey();
            int required = entry.getValue();
            int available = tempResources.getOrDefault(resource, 0);
            if (required > available) {
                return false;
            }
        }
        return true;
    }

    private void preemptTask(Task task) {
        releaseResources(task.getId());
        pendingTasks.add(task);
    }

    public synchronized void releaseResources(String taskId) {
        Task task = activeTasks.remove(taskId);
        if (task != null) {
            for (Map.Entry<String, Integer> entry : task.getRequirements().entrySet()) {
                String resource = entry.getKey();
                int released = entry.getValue();
                availableResources.merge(resource, released, Integer::sum);
            }
        }
    }

    public Map<String, Integer> getAvailableResources() {
        return new HashMap<>(availableResources);
    }

    public boolean isTaskActive(String taskId) {
        return activeTasks.containsKey(taskId);
    }

    private static class Task {
        private final String id;
        private final int priority;
        private final Map<String, Integer> requirements;
        private final long arrivalTime;
        private final long deadline;
        private final long executionTime;

        public Task(String id, int priority, Map<String, Integer> requirements, 
                long arrivalTime, long deadline, long executionTime) {
            this.id = id;
            this.priority = priority;
            this.requirements = new HashMap<>(requirements);
            this.arrivalTime = arrivalTime;
            this.deadline = deadline;
            this.executionTime = executionTime;
        }

        public String getId() {
            return id;
        }

        public int getPriority() {
            return priority;
        }

        public Map<String, Integer> getRequirements() {
            return new HashMap<>(requirements);
        }

        public long getArrivalTime() {
            return arrivalTime;
        }

        public long getDeadline() {
            return deadline;
        }

        public long getExecutionTime() {
            return executionTime;
        }
    }
}