import java.util.*;

public class TaskScheduler {

    static class Task {
        int id;
        int duration;
        int deadline;
        List<Integer> dependents;
        int inDegree;

        public Task(int id, int duration, int deadline) {
            this.id = id;
            this.duration = duration;
            this.deadline = deadline;
            this.dependents = new ArrayList<>();
            this.inDegree = 0;
        }
    }

    public static int calculateMinimumLateness(int N, int[] ids, int[] durations, int[] deadlines, List<List<Integer>> dependencies) {
        // Build tasks map and initialize tasks.
        Map<Integer, Task> tasks = new HashMap<>();
        for (int i = 0; i < N; i++) {
            tasks.put(ids[i], new Task(ids[i], durations[i], deadlines[i]));
        }
        
        // Build dependency graph.
        for (int i = 0; i < N; i++) {
            List<Integer> deps = dependencies.get(i);
            for (Integer dep : deps) {
                Task dependencyTask = tasks.get(dep);
                if (dependencyTask != null) {
                    dependencyTask.dependents.add(ids[i]);
                    Task currentTask = tasks.get(ids[i]);
                    currentTask.inDegree++;
                }
            }
        }
        
        // Use a priority queue to determine scheduling order among available tasks.
        // Prioritize tasks with earlier deadlines; tie-break with lower duration.
        PriorityQueue<Task> available = new PriorityQueue<>(new Comparator<Task>() {
            @Override
            public int compare(Task t1, Task t2) {
                if (t1.deadline != t2.deadline) {
                    return Integer.compare(t1.deadline, t2.deadline);
                }
                return Integer.compare(t1.duration, t2.duration);
            }
        });
        
        for (Task task : tasks.values()) {
            if (task.inDegree == 0) {
                available.offer(task);
            }
        }
        
        int currentTime = 0;
        int totalLateness = 0;
        int countScheduled = 0;
        
        while (!available.isEmpty()) {
            Task currentTask = available.poll();
            currentTime += currentTask.duration;
            int lateness = Math.max(0, currentTime - currentTask.deadline);
            totalLateness += lateness;
            countScheduled++;
            
            for (int dependentId : currentTask.dependents) {
                Task dependentTask = tasks.get(dependentId);
                dependentTask.inDegree--;
                if (dependentTask.inDegree == 0) {
                    available.offer(dependentTask);
                }
            }
        }
        
        if (countScheduled != N) {
            throw new IllegalArgumentException("Cycle detected in dependencies");
        }
        return totalLateness;
    }
    
    public static void main(String[] args) {
        // Sample usage:
        int N = 3;
        int[] ids = {0, 1, 2};
        int[] durations = {2, 3, 2};
        int[] deadlines = {5, 7, 9};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());        // Task 0: no dependencies.
        dependencies.add(Arrays.asList(0));           // Task 1 depends on Task 0.
        dependencies.add(Arrays.asList(1));           // Task 2 depends on Task 1.
        
        int result = calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        System.out.println("Total Lateness: " + result);
    }
}