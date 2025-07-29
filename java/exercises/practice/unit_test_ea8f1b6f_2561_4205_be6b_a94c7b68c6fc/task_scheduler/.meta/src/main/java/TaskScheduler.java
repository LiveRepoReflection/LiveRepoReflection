import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TaskScheduler {

    public Map<Integer, List<Task>> schedule(List<Task> tasks, List<Worker> workers) {
        Map<Integer, List<Task>> schedule = new HashMap<>();
        Map<Integer, Integer> finishingTime = new HashMap<>();
        for (Worker w : workers) {
            schedule.put(w.getWorkerId(), new ArrayList<>());
            finishingTime.put(w.getWorkerId(), 0);
        }

        // Build task map for quick access and prepare dependency graph support.
        Map<Integer, Task> taskMap = new HashMap<>();
        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.getTaskId(), t);
            graph.put(t.getTaskId(), new ArrayList<>());
            inDegree.put(t.getTaskId(), 0);
        }

        // Construct the dependency graph.
        for (Task t : tasks) {
            for (Integer dep : t.getDependencies()) {
                List<Integer> list = graph.get(dep);
                if (list != null) {
                    list.add(t.getTaskId());
                }
                inDegree.put(t.getTaskId(), inDegree.get(t.getTaskId()) + 1);
            }
        }

        // Initialize the ready list with tasks having no dependencies.
        List<Task> ready = new ArrayList<>();
        for (Task t : tasks) {
            if (inDegree.get(t.getTaskId()) == 0) {
                ready.add(t);
            }
        }

        // Process tasks in topological order.
        while (!ready.isEmpty()) {
            // Sort ready tasks by estimated execution time descending and then by dependency count descending.
            ready.sort((a, b) -> {
                if (b.getEstimatedExecutionTime() != a.getEstimatedExecutionTime()) {
                    return Integer.compare(b.getEstimatedExecutionTime(), a.getEstimatedExecutionTime());
                } else {
                    return Integer.compare(b.getDependencies().size(), a.getDependencies().size());
                }
            });

            Task current = ready.remove(0);
            Worker selectedWorker = null;
            int minFinish = Integer.MAX_VALUE;
            // Select the worker that can execute the task and currently has the smallest finishing time.
            for (Worker w : workers) {
                if (w.canRun(current)) {
                    int finishTime = finishingTime.get(w.getWorkerId());
                    if (finishTime < minFinish) {
                        minFinish = finishTime;
                        selectedWorker = w;
                    }
                }
            }

            // If no worker is capable of running the task, return an empty schedule.
            if (selectedWorker == null) {
                return new HashMap<>();
            }

            // Assign the task to the selected worker.
            schedule.get(selectedWorker.getWorkerId()).add(current);
            finishingTime.put(selectedWorker.getWorkerId(), finishingTime.get(selectedWorker.getWorkerId()) + current.getEstimatedExecutionTime());

            // Update the dependency graph.
            for (Integer neighbor : graph.get(current.getTaskId())) {
                inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                if (inDegree.get(neighbor) == 0) {
                    ready.add(taskMap.get(neighbor));
                }
            }
        }

        // Verify that all tasks are scheduled if not, return an empty schedule.
        if (countScheduledTasks(schedule) != tasks.size()) {
            return new HashMap<>();
        }
        return schedule;
    }

    private int countScheduledTasks(Map<Integer, List<Task>> schedule) {
        int count = 0;
        for (List<Task> taskList : schedule.values()) {
            count += taskList.size();
        }
        return count;
    }
}