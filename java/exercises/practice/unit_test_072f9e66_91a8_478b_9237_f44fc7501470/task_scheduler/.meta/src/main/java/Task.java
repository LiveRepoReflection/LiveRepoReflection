import java.util.List;
import java.util.Map;

public class Task {
    private final String id;
    private final int executionTime;
    private final int deadline;
    private final List<String> dependencies;
    private final Map<String, Integer> resourceRequirements;
    
    public Task(String id, int executionTime, int deadline, List<String> dependencies, 
                Map<String, Integer> resourceRequirements) {
        this.id = id;
        this.executionTime = executionTime;
        this.deadline = deadline;
        this.dependencies = dependencies;
        this.resourceRequirements = resourceRequirements;
    }
    
    public String getId() {
        return id;
    }
    
    public int getExecutionTime() {
        return executionTime;
    }
    
    public int getDeadline() {
        return deadline;
    }
    
    public List<String> getDependencies() {
        return dependencies;
    }
    
    public Map<String, Integer> getResourceRequirements() {
        return resourceRequirements;
    }
    
    @Override
    public String toString() {
        return "Task{" +
                "id='" + id + '\'' +
                ", executionTime=" + executionTime +
                ", deadline=" + deadline +
                ", dependencies=" + dependencies +
                ", resourceRequirements=" + resourceRequirements +
                '}';
    }
}