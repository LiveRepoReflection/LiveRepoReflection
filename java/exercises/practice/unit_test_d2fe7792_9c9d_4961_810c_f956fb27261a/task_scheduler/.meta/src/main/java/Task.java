import java.util.List;

public class Task implements Comparable<Task> {
    private String taskId;
    private Resource requiredResource;
    private String command;
    private List<String> dependencies;
    private int priority;
    private long submissionTime;
    private TaskStatus status;
    private String assignedWorker;
    private int retryCount;

    public Task(String taskId, Resource requiredResource, String command, List<String> dependencies, int priority) {
        this.taskId = taskId;
        this.requiredResource = requiredResource;
        this.command = command;
        this.dependencies = dependencies;
        this.priority = priority;
        this.status = TaskStatus.PENDING;
        this.assignedWorker = null;
        this.retryCount = 0;
    }

    public String getTaskId() {
        return taskId;
    }

    public Resource getRequiredResource() {
        return requiredResource;
    }

    public String getCommand() {
        return command;
    }

    public List<String> getDependencies() {
        return dependencies;
    }

    public int getPriority() {
        return priority;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public void setStatus(TaskStatus status) {
        this.status = status;
    }

    public long getSubmissionTime() {
        return submissionTime;
    }

    public void setSubmissionTime(long submissionTime) {
        this.submissionTime = submissionTime;
    }

    public String getAssignedWorker() {
        return assignedWorker;
    }

    public void setAssignedWorker(String assignedWorker) {
        this.assignedWorker = assignedWorker;
    }

    public int getRetryCount() {
        return retryCount;
    }

    public void incrementRetryCount() {
        this.retryCount++;
    }

    @Override
    public int compareTo(Task other) {
        if (this.priority != other.priority) {
            return Integer.compare(other.priority, this.priority);
        }
        return Long.compare(this.submissionTime, other.submissionTime);
    }
}