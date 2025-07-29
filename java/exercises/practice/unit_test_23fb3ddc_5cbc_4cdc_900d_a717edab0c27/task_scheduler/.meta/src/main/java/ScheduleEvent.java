public class ScheduleEvent {
    public int taskId;
    public int coreId;
    public int startTime;
    public int endTime;

    public ScheduleEvent(int taskId, int coreId, int startTime, int endTime) {
        this.taskId = taskId;
        this.coreId = coreId;
        this.startTime = startTime;
        this.endTime = endTime;
    }
}