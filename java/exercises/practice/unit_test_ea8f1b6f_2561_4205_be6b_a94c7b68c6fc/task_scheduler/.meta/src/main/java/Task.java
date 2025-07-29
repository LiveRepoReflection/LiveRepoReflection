import java.util.ArrayList;
import java.util.List;

public class Task {
    private int taskId;
    private int cpuRequired;
    private int memoryRequired;
    private int networkBandwidthRequired;
    private List<Integer> dependencies;
    private int estimatedExecutionTime;

    public Task(int taskId, int cpuRequired, int memoryRequired, int networkBandwidthRequired, List<Integer> dependencies, int estimatedExecutionTime) {
        this.taskId = taskId;
        this.cpuRequired = cpuRequired;
        this.memoryRequired = memoryRequired;
        this.networkBandwidthRequired = networkBandwidthRequired;
        this.dependencies = new ArrayList<>(dependencies);
        this.estimatedExecutionTime = estimatedExecutionTime;
    }

    public int getTaskId() {
        return taskId;
    }

    public int getCpuRequired() {
        return cpuRequired;
    }

    public int getMemoryRequired() {
        return memoryRequired;
    }

    public int getNetworkBandwidthRequired() {
        return networkBandwidthRequired;
    }

    public List<Integer> getDependencies() {
        return dependencies;
    }

    public int getEstimatedExecutionTime() {
        return estimatedExecutionTime;
    }
}