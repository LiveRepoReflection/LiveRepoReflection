public class Task {
    public final String id;
    public final int cpuCoresRequired;
    public final long memoryRequired;
    public final long diskSpaceRequired;
    public final long estimatedRunTime;
    
    public Task(String id, int cpuCoresRequired, long memoryRequired, long diskSpaceRequired, long estimatedRunTime) {
        this.id = id;
        this.cpuCoresRequired = cpuCoresRequired;
        this.memoryRequired = memoryRequired;
        this.diskSpaceRequired = diskSpaceRequired;
        this.estimatedRunTime = estimatedRunTime;
    }
}