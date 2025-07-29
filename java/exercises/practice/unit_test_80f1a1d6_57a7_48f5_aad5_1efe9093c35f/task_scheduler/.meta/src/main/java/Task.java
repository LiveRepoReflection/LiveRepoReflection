public class Task {
    private final int cpuCoresRequired;
    private final int memoryGBRequired;
    private final int gpuCountRequired;
    private final int executionTimeSeconds;

    public Task(int cpuCoresRequired, int memoryGBRequired, int gpuCountRequired, int executionTimeSeconds) {
        this.cpuCoresRequired = cpuCoresRequired;
        this.memoryGBRequired = memoryGBRequired;
        this.gpuCountRequired = gpuCountRequired;
        this.executionTimeSeconds = executionTimeSeconds;
    }

    public int getCpuCoresRequired() {
        return cpuCoresRequired;
    }

    public int getMemoryGBRequired() {
        return memoryGBRequired;
    }

    public int getGpuCountRequired() {
        return gpuCountRequired;
    }

    public int getExecutionTimeSeconds() {
        return executionTimeSeconds;
    }
}