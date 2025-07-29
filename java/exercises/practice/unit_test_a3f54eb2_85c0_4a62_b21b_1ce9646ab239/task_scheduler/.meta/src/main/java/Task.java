import java.util.List;

public class Task {
    int id;
    double processing_time;
    double deadline;
    List<Integer> dependencies;
    
    public Task(int id, double processing_time, double deadline, List<Integer> dependencies) {
        this.id = id;
        this.processing_time = processing_time;
        this.deadline = deadline;
        this.dependencies = dependencies;
    }
}