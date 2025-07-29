package task_scheduler;

import java.util.List;
import java.util.ArrayList;

public class Task {
    private int id;
    private int duration;
    private int deadline;
    private List<Integer> dependencies;

    public Task(int id, int duration, int deadline, List<Integer> dependencies) {
        this.id = id;
        this.duration = duration;
        this.deadline = deadline;
        if (dependencies == null) {
            this.dependencies = new ArrayList<>();
        } else {
            this.dependencies = dependencies;
        }
    }

    public int getId() {
        return id;
    }

    public int getDuration() {
        return duration;
    }

    public int getDeadline() {
        return deadline;
    }

    public List<Integer> getDependencies() {
        return dependencies;
    }
}