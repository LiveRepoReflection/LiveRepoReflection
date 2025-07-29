import java.util.Map;
import java.util.Set;

public class Task {
    private String taskId;
    private Map<String, Integer> resourceRequirements;
    private long dataSize;
    private int priority;
    private Set<String> dependencies;
    
    public Task(String taskId, Map<String, Integer> resourceRequirements, 
                long dataSize, int priority, Set<String> dependencies) {
        this.taskId = taskId;
        this.resourceRequirements = resourceRequirements;
        this.dataSize = dataSize;
        this.priority = priority;
        this.dependencies = dependencies;
    }
    
    public String getTaskId() { return taskId; }
    public Map<String, Integer> getResourceRequirements() { return resourceRequirements; }
    public long getDataSize() { return dataSize; }
    public int getPriority() { return priority; }
    public Set<String> getDependencies() { return dependencies; }
}