import java.util.List;

public class Task {
    private final int id;
    private final int duration;
    private final int deadline;
    private final List<Integer> dependencies;

    public Task(int id, int duration, int deadline, List<Integer> dependencies) {
        this.id = id;
        this.duration = duration;
        this.deadline = deadline;
        this.dependencies = dependencies;
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