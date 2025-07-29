import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.TreeSet;
import java.util.Collections;

public class TaskScheduler {

    public static List<ScheduledTask> scheduleTasks(List<Machine> machines, List<Task> tasks, int maxConcurrentTasksPerMachine) {
        // Build a mapping from task id to Task for easy lookup.
        Map<String, Task> tasksMap = new HashMap<>();
        for (Task t : tasks) {
            tasksMap.put(t.id, t);
        }

        // For each machine, maintain its own schedule.
        Map<String, List<ScheduledTask>> machineSchedules = new HashMap<>();
        for (Machine m : machines) {
            machineSchedules.put(m.id, new ArrayList<>());
        }

        List<ScheduledTask> result = new ArrayList<>();

        // Greedily schedule each task in the order provided.
        for (Task t : tasks) {
            ScheduledTask bestScheduledTask = null;
            long bestFinishTime = Long.MAX_VALUE;
            String bestMachineId = null;
            long bestCandidateStart = Long.MAX_VALUE;

            // Try scheduling on each machine
            for (Machine m : machines) {
                List<ScheduledTask> currentSchedule = machineSchedules.get(m.id);
                long candidateStart = findEarliestStart(m, currentSchedule, t, maxConcurrentTasksPerMachine, tasksMap);
                long finishTime = candidateStart + t.estimatedRunTime;
                
                if (finishTime < bestFinishTime ||
                    (finishTime == bestFinishTime && (bestMachineId == null || m.id.compareTo(bestMachineId) < 0))) {
                    bestFinishTime = finishTime;
                    bestMachineId = m.id;
                    bestCandidateStart = candidateStart;
                    bestScheduledTask = new ScheduledTask(t.id, m.id, candidateStart);
                }
            }
            result.add(bestScheduledTask);
            machineSchedules.get(bestScheduledTask.machineId).add(bestScheduledTask);
        }
        return result;
    }

    // Finds the earliest start time on machine m for task t given the machine's current schedule.
    private static long findEarliestStart(Machine m, List<ScheduledTask> scheduled, Task t, int maxConcurrentTasksPerMachine, Map<String, Task> tasksMap) {
        TreeSet<Long> candidateTimes = new TreeSet<>();
        candidateTimes.add(0L);
        // Add finish times of all scheduled tasks as potential candidate times.
        for (ScheduledTask st : scheduled) {
            Task other = tasksMap.get(st.taskId);
            long finish = st.startTime + other.estimatedRunTime;
            candidateTimes.add(finish);
        }
        // Try candidate times first.
        for (long candidate : candidateTimes) {
            if (isValidInterval(m, scheduled, candidate, candidate + t.estimatedRunTime, t, maxConcurrentTasksPerMachine, tasksMap)) {
                return candidate;
            }
        }
        // If none of the candidate times work, start from the last candidate and increment by 1 ms until valid.
        long candidate = candidateTimes.last();
        while (true) {
            if (isValidInterval(m, scheduled, candidate, candidate + t.estimatedRunTime, t, maxConcurrentTasksPerMachine, tasksMap)) {
                return candidate;
            }
            candidate++;
        }
    }

    // Checks if scheduling task newTask in the interval [start, end) on machine m is valid given current scheduled tasks.
    private static boolean isValidInterval(Machine m, List<ScheduledTask> scheduled, long start, long end, Task newTask, int maxConcurrentTasksPerMachine, Map<String, Task> tasksMap) {
        // Gather relevant time points: start, end, and boundaries from overlapping tasks.
        List<Long> timePoints = new ArrayList<>();
        timePoints.add(start);
        timePoints.add(end);
        for (ScheduledTask st : scheduled) {
            Task other = tasksMap.get(st.taskId);
            long otherStart = st.startTime;
            long otherEnd = st.startTime + other.estimatedRunTime;
            if (otherEnd > start && otherStart < end) {
                timePoints.add(Math.max(start, otherStart));
                timePoints.add(Math.min(end, otherEnd));
            }
        }
        Collections.sort(timePoints);
        // Remove duplicate time points.
        List<Long> uniqueTimePoints = new ArrayList<>();
        uniqueTimePoints.add(timePoints.get(0));
        for (int i = 1; i < timePoints.size(); i++) {
            if (!timePoints.get(i).equals(timePoints.get(i - 1))) {
                uniqueTimePoints.add(timePoints.get(i));
            }
        }

        // For each interval between consecutive time points, check if adding newTask violates resource constraints.
        for (int i = 0; i < uniqueTimePoints.size() - 1; i++) {
            long tSample = uniqueTimePoints.get(i);
            int cpuUsed = 0;
            long memUsed = 0;
            long diskUsed = 0;
            int concurrent = 0;
            // Sum resource usage of tasks active at tSample.
            for (ScheduledTask st : scheduled) {
                Task other = tasksMap.get(st.taskId);
                long s = st.startTime;
                long e = st.startTime + other.estimatedRunTime;
                if (tSample >= s && tSample < e) {
                    cpuUsed += other.cpuCoresRequired;
                    memUsed += other.memoryRequired;
                    diskUsed += other.diskSpaceRequired;
                    concurrent++;
                }
            }
            // Include the new task's resource usage.
            cpuUsed += newTask.cpuCoresRequired;
            memUsed += newTask.memoryRequired;
            diskUsed += newTask.diskSpaceRequired;
            concurrent += 1;
            
            if (cpuUsed > m.cpuCores || memUsed > m.memory || diskUsed > m.diskSpace || concurrent > maxConcurrentTasksPerMachine) {
                return false;
            }
        }
        return true;
    }
}