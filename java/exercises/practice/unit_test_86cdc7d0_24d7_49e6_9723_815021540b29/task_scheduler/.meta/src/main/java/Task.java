import java.util.ArrayList;
import java.util.List;

public class Task {
    private int id;
    private int priority;
    private List<Integer> dependencies;
    private int executionTime;

    public Task(int id, int priority, List<Integer> dependencies, int executionTime) {
        this.id = id;
        this.priority = priority;
        this.dependencies = new ArrayList<>(dependencies);
        this.executionTime = executionTime;
    }

    public int getId() {
        return id;
    }

    public int getPriority() {
        return priority;
    }

    public List<Integer> getDependencies() {
        return dependencies;
    }

    public int getExecutionTime() {
        return executionTime;
    }
}