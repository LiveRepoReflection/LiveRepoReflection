import java.util.ArrayList;
import java.util.List;

public class Task {
    public int id;
    public int duration;
    public int deadline;
    public List<Integer> dependencies;
    public List<Task> successors;

    public Task(int id, int duration, int deadline, List<Integer> dependencies) {
        this.id = id;
        this.duration = duration;
        this.deadline = deadline;
        this.dependencies = new ArrayList<>(dependencies);
        this.successors = new ArrayList<>();
    }
}