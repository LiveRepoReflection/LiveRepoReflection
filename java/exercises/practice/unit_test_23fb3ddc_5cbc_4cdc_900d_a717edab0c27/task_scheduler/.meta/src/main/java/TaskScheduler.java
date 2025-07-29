import java.util.*;

public class TaskScheduler {

    public static List<ScheduleEvent> scheduleTasks(List<Task> tasks, int numCores) {
        if (tasks == null || tasks.isEmpty() || numCores <= 0) {
            return new ArrayList<>();
        }

        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.id, task);
        }

        Map<Integer, List<Integer>> graph = new HashMap<>();
        Map<Integer, Integer> inDegree = new HashMap<>();
        for (Task task : tasks) {
            inDegree.put(task.id, 0);
            graph.put(task.id, new ArrayList<>());
        }
        for (Task task : tasks) {
            for (Integer dep : task.dependencies) {
                graph.get(dep).add(task.id);
                inDegree.put(task.id, inDegree.get(task.id) + 1);
            }
        }

        Map<Integer, Integer> earliestStart = new HashMap<>();
        for (Task task : tasks) {
            earliestStart.put(task.id, 0);
        }

        PriorityQueue<Task> readyQueue = new PriorityQueue<>(new Comparator<Task>() {
            public int compare(Task t1, Task t2) {
                int es1 = earliestStart.get(t1.id);
                int es2 = earliestStart.get(t2.id);
                if (es1 != es2) {
                    return Integer.compare(es1, es2);
                }
                if (t1.deadline != t2.deadline) {
                    return Integer.compare(t1.deadline, t2.deadline);
                }
                return Integer.compare(t1.id, t2.id);
            }
        });

        for (Task task : tasks) {
            if (inDegree.get(task.id) == 0) {
                readyQueue.offer(task);
            }
        }

        PriorityQueue<Core> coreQueue = new PriorityQueue<>(new Comparator<Core>() {
            public int compare(Core c1, Core c2) {
                if (c1.availableTime != c2.availableTime) {
                    return Integer.compare(c1.availableTime, c2.availableTime);
                }
                return Integer.compare(c1.coreId, c2.coreId);
            }
        });
        for (int i = 0; i < numCores; i++) {
            coreQueue.offer(new Core(i, 0));
        }

        List<ScheduleEvent> schedule = new ArrayList<>();
        int scheduledCount = 0;
        while (!readyQueue.isEmpty()) {
            Task currentTask = readyQueue.poll();
            Core core = coreQueue.poll();
            int startTime = Math.max(core.availableTime, earliestStart.get(currentTask.id));
            int finishTime = startTime + currentTask.duration;
            if (finishTime > currentTask.deadline) {
                return null;
            }
            ScheduleEvent event = new ScheduleEvent(currentTask.id, core.coreId, startTime, finishTime);
            schedule.add(event);
            scheduledCount++;
            core.availableTime = finishTime;
            coreQueue.offer(core);

            List<Integer> children = graph.get(currentTask.id);
            for (Integer childId : children) {
                int childES = earliestStart.get(childId);
                earliestStart.put(childId, Math.max(childES, finishTime));
                inDegree.put(childId, inDegree.get(childId) - 1);
                if (inDegree.get(childId) == 0) {
                    readyQueue.offer(taskMap.get(childId));
                }
            }
        }
        if (scheduledCount != tasks.size()) {
            return null;
        }
        schedule.sort(new Comparator<ScheduleEvent>() {
            public int compare(ScheduleEvent e1, ScheduleEvent e2) {
                return Integer.compare(e1.startTime, e2.startTime);
            }
        });
        return schedule;
    }

    static class Core {
        int coreId;
        int availableTime;

        Core(int coreId, int availableTime) {
            this.coreId = coreId;
            this.availableTime = availableTime;
        }
    }
}