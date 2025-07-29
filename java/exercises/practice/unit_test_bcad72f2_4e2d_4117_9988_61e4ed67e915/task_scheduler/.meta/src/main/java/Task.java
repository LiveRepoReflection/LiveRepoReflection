import java.util.Set;

public class Task {
    private String id;
    private int cpuRequirement;
    private int memoryRequirement;
    private int diskRequirement;
    private Set<String> dependencies;
    private int estimatedRunTime;

    public Task(String id, int cpuRequirement, int memoryRequirement, int diskRequirement, Set<String> dependencies, int estimatedRunTime) {
        this.id = id;
        this.cpuRequirement = cpuRequirement;
        this.memoryRequirement = memoryRequirement;
        this.diskRequirement = diskRequirement;
        this.dependencies = dependencies;
        this.estimatedRunTime = estimatedRunTime;
    }

    public String getId() {
        return id;
    }

    public int getCpuRequirement() {
        return cpuRequirement;
    }

    public int getMemoryRequirement() {
        return memoryRequirement;
    }

    public int getDiskRequirement() {
        return diskRequirement;
    }

    public Set<String> getDependencies() {
        return dependencies;
    }

    public int getEstimatedRunTime() {
        return estimatedRunTime;
    }
}