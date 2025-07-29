import java.util.List;

public class Task {
    int id;
    int duration;
    int deadline;
    int penalty;
    List<Integer> dependencies; // List of task IDs that must be completed before this task

    public Task(int id, int duration, int deadline, int penalty, List<Integer> dependencies) {
        this.id = id;
        this.duration = duration;
        this.deadline = deadline;
        this.penalty = penalty;
        this.dependencies = dependencies;
    }
}