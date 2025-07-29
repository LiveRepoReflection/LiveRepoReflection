import java.util.Set;

public class Task {
    public String id;
    public int cpuCores;
    public int memory;
    public int executionTime;
    public Set<String> dependencies;

    public Task(String id, int cpuCores, int memory, int executionTime, Set<String> dependencies) {
        this.id = id;
        this.cpuCores = cpuCores;
        this.memory = memory;
        this.executionTime = executionTime;
        this.dependencies = dependencies;
    }
}