import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.Comparator;
import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    // Helper classes assumed to exist in the main package:
    // Machine, Task, ScheduledTask, and TaskScheduler with method:
    // SchedulingResult scheduleTasks(List<Machine> machines, List<Task> tasks, int maxConcurrentTasksPerMachine)
    // For the purpose of testing, we compute the makespan as the maximum of (startTime + estimatedRunTime)
    // for all scheduled tasks.

    // We'll create separate helper methods to validate the scheduling constraints.

    private static class Event {
        long time;
        int cpuDelta;
        long memoryDelta;
        long diskDelta;
        int concurrencyDelta;
        
        Event(long time, int cpuDelta, long memoryDelta, long diskDelta, int concurrencyDelta) {
            this.time = time;
            this.cpuDelta = cpuDelta;
            this.memoryDelta = memoryDelta;
            this.diskDelta = diskDelta;
            this.concurrencyDelta = concurrencyDelta;
        }
    }
    
    private void validateSchedule(List<Machine> machines, List<Task> tasks, List<ScheduledTask> scheduledTasks, int maxConcurrentTasksPerMachine) {
        // Map machine id to Machine
        Map<String, Machine> machineMap = new HashMap<>();
        for (Machine m : machines) {
            machineMap.put(m.id, m);
        }
        
        // Map task id to Task
        Map<String, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.id, t);
        }
        
        // Validate that every task is scheduled exactly once.
        assertEquals(tasks.size(), scheduledTasks.size(), "Not all tasks were scheduled");
        // Use a set to track scheduled task ids.
        Map<String, Integer> taskCount = new HashMap<>();
        for (ScheduledTask st : scheduledTasks) {
            taskCount.put(st.taskId, taskCount.getOrDefault(st.taskId, 0) + 1);
        }
        for (Task t : tasks) {
            assertEquals(1, taskCount.getOrDefault(t.id, 0), "Task " + t.id + " is scheduled more than once or missing");
        }
        
        // Validate that scheduled tasks satisfy resource and concurrent constraints per machine.
        // For each machine, create events for task start (+ usage) and finish (- usage).
        Map<String, List<Event>> machineEvents = new HashMap<>();
        for (ScheduledTask st : scheduledTasks) {
            Machine machine = machineMap.get(st.machineId);
            assertNotNull(machine, "Machine " + st.machineId + " not found");
            Task task = taskMap.get(st.taskId);
            assertNotNull(task, "Task " + st.taskId + " not found");
            
            long startTime = st.startTime;
            long finishTime = st.startTime + task.estimatedRunTime;
            // Add events to the machine's event list.
            machineEvents.putIfAbsent(machine.id, new ArrayList<>());
            // Start event: add resource usage and increment concurrent count.
            machineEvents.get(machine.id).add(new Event(startTime, task.cpuCoresRequired, task.memoryRequired, task.diskSpaceRequired, 1));
            // Finish event: subtract resource usage and decrement concurrent count.
            machineEvents.get(machine.id).add(new Event(finishTime, -task.cpuCoresRequired, -task.memoryRequired, -task.diskSpaceRequired, -1));
            
            // Additionally, a task must start at time >= 0.
            assertTrue(startTime >= 0, "Task " + task.id + " has negative start time");
        }
        
        // For each machine, process events in time order.
        for (Map.Entry<String, List<Event>> entry : machineEvents.entrySet()) {
            String machineId = entry.getKey();
            Machine machine = machineMap.get(machineId);
            List<Event> events = entry.getValue();
            // Sort events by time; if same time, process finish events (- delta) before start events (+ delta)
            Collections.sort(events, new Comparator<Event>() {
                @Override
                public int compare(Event e1, Event e2) {
                    if (e1.time != e2.time) {
                        return Long.compare(e1.time, e2.time);
                    } else {
                        // finish events should come before start events
                        return Integer.compare(e1.concurrencyDelta, e2.concurrencyDelta);
                    }
                }
            });
            
            int currentConcurrency = 0;
            int currentCpu = 0;
            long currentMemory = 0;
            long currentDisk = 0;
            for (Event event : events) {
                currentConcurrency += event.concurrencyDelta;
                currentCpu += event.cpuDelta;
                currentMemory += event.memoryDelta;
                currentDisk += event.diskDelta;
                // Validate concurrent tasks count does not exceed maximum.
                assertTrue(currentConcurrency <= maxConcurrentTasksPerMachine, "Machine " + machineId + " exceeds max concurrent tasks at time " + event.time);
                // Validate resource usage does not exceed available machine resources.
                assertTrue(currentCpu <= machine.cpuCores, "Machine " + machineId + " exceeds CPU capacity at time " + event.time);
                assertTrue(currentMemory <= machine.memory, "Machine " + machineId + " exceeds memory capacity at time " + event.time);
                assertTrue(currentDisk <= machine.diskSpace, "Machine " + machineId + " exceeds disk space at time " + event.time);
            }
        }
    }
    
    private long computeMakespan(List<Task> tasks, List<ScheduledTask> scheduledTasks) {
        Map<String, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.id, t);
        }
        long makespan = 0;
        for (ScheduledTask st : scheduledTasks) {
            Task task = taskMap.get(st.taskId);
            long finishTime = st.startTime + task.estimatedRunTime;
            if (finishTime > makespan) {
                makespan = finishTime;
            }
        }
        return makespan;
    }
    
    @Test
    public void testEmptySchedule() {
        List<Machine> machines = new ArrayList<>();
        machines.add(new Machine("machine-1", 4, 16000L, 100000L));
        
        List<Task> tasks = new ArrayList<>();
        int maxConcurrentTasksPerMachine = 2;
        
        List<ScheduledTask> scheduledTasks = TaskScheduler.scheduleTasks(machines, tasks, maxConcurrentTasksPerMachine);
        // Expect an empty schedule.
        assertNotNull(scheduledTasks, "Scheduled tasks list should not be null");
        assertEquals(0, scheduledTasks.size(), "No tasks should be scheduled");
        
        long makespan = computeMakespan(tasks, scheduledTasks);
        assertEquals(0, makespan, "Makespan for empty schedule should be 0");
    }
    
    @Test
    public void testSingleTaskSchedule() {
        List<Machine> machines = new ArrayList<>();
        machines.add(new Machine("machine-1", 4, 16000L, 100000L));
        
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task("task-1", 2, 8000L, 50000L, 5000L));
        
        int maxConcurrentTasksPerMachine = 2;
        List<ScheduledTask> scheduledTasks = TaskScheduler.scheduleTasks(machines, tasks, maxConcurrentTasksPerMachine);
        
        // Validate the schedule
        assertEquals(1, scheduledTasks.size(), "There should be one scheduled task");
        ScheduledTask st = scheduledTasks.get(0);
        assertEquals("task-1", st.taskId, "Scheduled task id should match");
        assertEquals("machine-1", st.machineId, "Scheduled machine id should match");
        // The task should start at time 0 for optimal schedule.
        assertEquals(0, st.startTime, "The task should start at time 0");
        
        // Validate overall schedule constraints
        validateSchedule(machines, tasks, scheduledTasks, maxConcurrentTasksPerMachine);
        
        long makespan = computeMakespan(tasks, scheduledTasks);
        assertEquals(5000L, makespan, "Makespan should equal the task run time");
    }
    
    @Test
    public void testMultipleTasksSequentialSchedule() {
        List<Machine> machines = new ArrayList<>();
        machines.add(new Machine("machine-1", 4, 16000L, 100000L));
        
        List<Task> tasks = new ArrayList<>();
        // Two tasks that fully utilize the machine so they cannot run concurrently.
        tasks.add(new Task("task-1", 4, 16000L, 100000L, 3000L));
        tasks.add(new Task("task-2", 4, 16000L, 100000L, 4000L));
        
        int maxConcurrentTasksPerMachine = 2;
        List<ScheduledTask> scheduledTasks = TaskScheduler.scheduleTasks(machines, tasks, maxConcurrentTasksPerMachine);
        
        // Validate schedule integrity
        assertEquals(2, scheduledTasks.size(), "There should be two scheduled tasks");
        validateSchedule(machines, tasks, scheduledTasks, maxConcurrentTasksPerMachine);
        
        // Check that tasks do not overlap in time on the same machine.
        // For tasks that fully occupy the machine, one should start after the other finishes.
        Map<String, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.id, t);
        }
        ScheduledTask st1 = scheduledTasks.get(0);
        ScheduledTask st2 = scheduledTasks.get(1);
        // Ensure both tasks are on the same machine.
        assertEquals(st1.machineId, st2.machineId, "Both tasks should be scheduled on the same machine");
        long finish1 = st1.startTime + taskMap.get(st1.taskId).estimatedRunTime;
        long finish2 = st2.startTime + taskMap.get(st2.taskId).estimatedRunTime;
        // One task must finish before the other starts.
        boolean sequential = (st1.startTime >= finish2) || (st2.startTime >= finish1);
        assertTrue(sequential, "Tasks should not overlap due to full resource utilization");
        
        long makespan = computeMakespan(tasks, scheduledTasks);
        // The optimal makespan should be the sum of durations.
        assertEquals(7000L, makespan, "Makespan should be the sum of task durations in sequential scheduling");
    }
    
    @Test
    public void testMultipleMachinesConcurrentSchedule() {
        List<Machine> machines = new ArrayList<>();
        machines.add(new Machine("machine-1", 4, 16000L, 100000L));
        machines.add(new Machine("machine-2", 8, 32000L, 200000L));
        
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task("task-1", 2, 8000L, 50000L, 5000L));
        tasks.add(new Task("task-2", 2, 8000L, 50000L, 3000L));
        tasks.add(new Task("task-3", 4, 16000L, 100000L, 4000L));
        
        int maxConcurrentTasksPerMachine = 2;
        List<ScheduledTask> scheduledTasks = TaskScheduler.scheduleTasks(machines, tasks, maxConcurrentTasksPerMachine);
        
        // Validate that all tasks are scheduled properly.
        assertEquals(3, scheduledTasks.size(), "There should be three scheduled tasks");
        validateSchedule(machines, tasks, scheduledTasks, maxConcurrentTasksPerMachine);
        
        // Check that tasks are distributed among machines such that the makespan is minimized.
        long makespan = computeMakespan(tasks, scheduledTasks);
        // In an optimal scenario, tasks should be scheduled concurrently on available machines.
        // Since exact ordering may vary, we validate that makespan does not exceed the sum of longest sequential tasks.
        long sumOfLongest = 5000L + 4000L; // worst-case if tasks on machine-1 and machine-2 sequentially
        assertTrue(makespan <= sumOfLongest, "Makespan should be reasonably optimized");
    }
}