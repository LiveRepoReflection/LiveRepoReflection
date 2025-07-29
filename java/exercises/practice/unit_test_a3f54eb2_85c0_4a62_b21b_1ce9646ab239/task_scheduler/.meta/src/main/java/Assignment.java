public class Assignment {
    int taskId;
    int workerId;
    double startTime;
    double endTime;
    
    public Assignment(int taskId, int workerId, double startTime, double endTime) {
        this.taskId = taskId;
        this.workerId = workerId;
        this.startTime = startTime;
        this.endTime = endTime;
    }
}