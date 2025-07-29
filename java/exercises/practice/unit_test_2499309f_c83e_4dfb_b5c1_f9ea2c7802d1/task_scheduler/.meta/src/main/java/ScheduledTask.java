public class ScheduledTask {
    public final String taskId;
    public final String machineId;
    public final long startTime;
    
    public ScheduledTask(String taskId, String machineId, long startTime) {
        this.taskId = taskId;
        this.machineId = machineId;
        this.startTime = startTime;
    }
}