package task_schedule;

import java.util.List;

public class Task {
    public int id;
    public int duration;
    public int deadline;
    public List<Integer> dependencies;

    public Task(int id, int duration, int deadline, List<Integer> dependencies) {
        this.id = id;
        this.duration = duration;
        this.deadline = deadline;
        this.dependencies = dependencies;
    }
}