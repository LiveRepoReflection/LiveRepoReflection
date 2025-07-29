import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.PriorityQueue;

public class TaskScheduler {
    public int[] scheduleTasks(int n, List<int[]> tasks) {
        if (n <= 0 || tasks == null || tasks.isEmpty()) {
            return new int[0];
        }

        // Create a priority queue to track worker load (makespan)
        PriorityQueue<Worker> workerQueue = new PriorityQueue<>(
            Comparator.comparingInt(Worker::getCurrentLoad)
            .thenComparingInt(Worker::getId)
        );

        // Initialize workers
        for (int i = 0; i < n; i++) {
            workerQueue.add(new Worker(i));
        }

        // Sort tasks by deadline (earliest first) then processing time (shortest first)
        int[][] sortedTasks = new int[tasks.size()][3];
        for (int i = 0; i < tasks.size(); i++) {
            sortedTasks[i][0] = tasks.get(i)[0]; // processing time
            sortedTasks[i][1] = tasks.get(i)[1]; // deadline
            sortedTasks[i][2] = i; // original index
        }

        Arrays.sort(sortedTasks, (a, b) -> {
            if (a[1] != b[1]) {
                return Integer.compare(a[1], b[1]); // earlier deadline first
            }
            return Integer.compare(a[0], b[0]); // shorter task first
        });

        int[] assignment = new int[tasks.size()];

        for (int[] task : sortedTasks) {
            int processingTime = task[0];
            int deadline = task[1];
            int taskIndex = task[2];

            Worker worker = workerQueue.poll();
            
            // Assign task to this worker
            assignment[taskIndex] = worker.getId();
            worker.addTask(processingTime);
            
            workerQueue.add(worker);
        }

        return assignment;
    }

    private static class Worker {
        private final int id;
        private int currentLoad;

        public Worker(int id) {
            this.id = id;
            this.currentLoad = 0;
        }

        public int getId() {
            return id;
        }

        public int getCurrentLoad() {
            return currentLoad;
        }

        public void addTask(int processingTime) {
            currentLoad += processingTime;
        }
    }
}