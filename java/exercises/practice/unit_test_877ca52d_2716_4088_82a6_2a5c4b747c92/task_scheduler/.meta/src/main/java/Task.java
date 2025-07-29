import java.util.ArrayList;
import java.util.List;

public class Task {
    public int taskId;
    public int duration;
    public int deadline;
    public List<Integer> dependencies;

    public Task(int taskId, int duration, int deadline, List<Integer> dependencies) {
        this.taskId = taskId;
        this.duration = duration;
        this.deadline = deadline;
        // Create a new list to avoid external modifications.
        this.dependencies = new ArrayList<>(dependencies);
    }
}