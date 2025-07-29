package task_scheduler;

import java.util.*;

public class TaskScheduler {

    /**
     * Returns the optimal schedule of task ids.
     *
     * @param N            the total number of tasks
     * @param id           array of task ids
     * @param duration     array of task durations
     * @param deadline     array of task deadlines
     * @param dependencies list of lists, where each inner list contains the ids of tasks that must
     *                     be completed before the corresponding task
     * @param priority     array of task priorities
     * @return an ordered list of task ids representing the optimal schedule
     */
    public static List<Integer> getOptimalSchedule(int N, int[] id, int[] duration, int[] deadline,
                                                     List<List<Integer>> dependencies, int[] priority) {
        // Build graph: for each task, list tasks that depend on it.
        List<List<Integer>> graph = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            graph.add(new ArrayList<>());
        }
        // inDegree count of prerequisites for each task.
        int[] inDegree = new int[N];
        for (int i = 0; i < N; i++) {
            for (int dep : dependencies.get(i)) {
                // task i depends on dep, so dep -> i in graph
                graph.get(dep).add(i);
                inDegree[i]++;
            }
        }

        // dropped flag, if a task is dropped, it and its descendants are not schedulable.
        boolean[] dropped = new boolean[N];

        // PriorityQueue for available tasks.
        // Comparator: first by deadline ascending; if deadlines equal, then by id descending.
        PriorityQueue<Integer> available = new PriorityQueue<>(new Comparator<Integer>() {
            @Override
            public int compare(Integer a, Integer b) {
                if (deadline[a] != deadline[b]) {
                    return Integer.compare(deadline[a], deadline[b]);
                } else {
                    return Integer.compare(b, a);
                }
            }
        });
        
        // Initially, add tasks with inDegree zero.
        for (int i = 0; i < N; i++) {
            if (inDegree[i] == 0) {
                available.add(i);
            }
        }

        int currentTime = 0;
        List<Integer> schedule = new ArrayList<>();

        while (!available.isEmpty()) {
            int task = available.poll();
            if (dropped[task]) {
                continue;
            }
            // Check if this task can be finished before its deadline.
            if (currentTime + duration[task] <= deadline[task]) {
                // Schedule the task.
                currentTime += duration[task];
                schedule.add(task);
                // For each dependent task, reduce inDegree.
                for (int dependent : graph.get(task)) {
                    inDegree[dependent]--;
                    if (inDegree[dependent] == 0 && !dropped[dependent]) {
                        available.add(dependent);
                    }
                }
            } else {
                // This task cannot be scheduled, drop it and all its descendants.
                dropTask(task, graph, dropped);
            }
        }
        return schedule;
    }

    // Recursively mark task and its descendants as dropped.
    private static void dropTask(int task, List<List<Integer>> graph, boolean[] dropped) {
        if (dropped[task]) {
            return;
        }
        dropped[task] = true;
        // Recursively drop all dependents.
        for (int dependent : graph.get(task)) {
            dropTask(dependent, graph, dropped);
        }
    }
}