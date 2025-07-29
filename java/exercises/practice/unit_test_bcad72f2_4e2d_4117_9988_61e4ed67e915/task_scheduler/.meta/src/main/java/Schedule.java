import java.util.Map;

public class Schedule {
    private Map<String, String> taskAssignments;
    private int makespan;

    public Schedule(Map<String, String> taskAssignments, int makespan) {
        this.taskAssignments = taskAssignments;
        this.makespan = makespan;
    }

    public Map<String, String> getTaskAssignments() {
        return taskAssignments;
    }

    public int getMakespan() {
        return makespan;
    }
}