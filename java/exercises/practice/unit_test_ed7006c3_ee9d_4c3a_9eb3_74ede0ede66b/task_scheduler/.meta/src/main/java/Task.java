import java.util.Map;

public class Task {
    private final String taskId;
    private final int priority;
    private final Map<String, Integer> resourceRequirements;
    private final int estimatedExecutionTime;
    private final String clientId;
    private TaskState state;
    private long submissionTime;
    
    public Task(String taskId, int priority, Map<String, Integer> resourceRequirements, int estimatedExecutionTime, String clientId) {
        this.taskId = taskId;
        this.priority = priority;
        this.resourceRequirements = resourceRequirements;
        this.estimatedExecutionTime = estimatedExecutionTime;
        this.clientId = clientId;
        this.state = TaskState.QUEUED;
    }
    
    public String getTaskId() {
        return taskId;
    }
    
    public int getPriority() {
        return priority;
    }
    
    public Map<String, Integer> getResourceRequirements() {
        return resourceRequirements;
    }
    
    public int getEstimatedExecutionTime() {
        return estimatedExecutionTime;
    }
    
    public String getClientId() {
        return clientId;
    }
    
    public TaskState getState() {
        return state;
    }
    
    public void setState(TaskState state) {
        this.state = state;
    }
    
    public long getSubmissionTime() {
        return submissionTime;
    }
    
    public void setSubmissionTime(long submissionTime) {
        this.submissionTime = submissionTime;
    }
}