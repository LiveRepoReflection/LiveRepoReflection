public class ScheduledTask {
    private int taskId;
    private int workerId;
    private int startTime;
    private int endTime;
    private String status;
    private int retries;

    public ScheduledTask(int taskId, int workerId, int startTime, int endTime, String status, int retries) {
        this.taskId = taskId;
        this.workerId = workerId;
        this.startTime = startTime;
        this.endTime = endTime;
        this.status = status;
        this.retries = retries;
    }

    public int getTaskId() {
        return taskId;
    }

    public int getWorkerId() {
        return workerId;
    }

    public int getStartTime() {
        return startTime;
    }

    public int getEndTime() {
        return endTime;
    }

    public String getStatus() {
        return status;
    }

    public int getRetries() {
        return retries;
    }
}