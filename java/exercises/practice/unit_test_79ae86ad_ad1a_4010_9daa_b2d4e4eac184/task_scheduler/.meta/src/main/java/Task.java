import java.util.Map;
import java.util.Objects;

public class Task {
    private final String taskId;
    private final int priority;
    private final long estimatedExecutionTime;
    private final Map<String, Integer> resourceRequirements;
    private final long arrivalTime;

    public Task(String taskId, int priority, long estimatedExecutionTime, 
                Map<String, Integer> resourceRequirements) {
        this.taskId = taskId;
        this.priority = priority;
        this.estimatedExecutionTime = estimatedExecutionTime;
        this.resourceRequirements = Map.copyOf(resourceRequirements);
        this.arrivalTime = System.currentTimeMillis();
    }

    public String getTaskId() { return taskId; }
    public int getPriority() { return priority; }
    public long getEstimatedExecutionTime() { return estimatedExecutionTime; }
    public Map<String, Integer> getResourceRequirements() { return resourceRequirements; }
    public long getDeadline() { return arrivalTime + estimatedExecutionTime; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Task task = (Task) o;
        return taskId.equals(task.taskId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(taskId);
    }
}