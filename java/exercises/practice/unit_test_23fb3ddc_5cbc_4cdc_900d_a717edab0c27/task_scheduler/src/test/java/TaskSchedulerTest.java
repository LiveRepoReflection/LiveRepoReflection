import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    // Helper method to verify that the schedule events are sorted by start time.
    private void assertSortedByStartTime(List<ScheduleEvent> schedule) {
        for (int i = 1; i < schedule.size(); i++) {
            assertTrue(schedule.get(i - 1).startTime <= schedule.get(i).startTime,
                "Schedule events are not sorted by start time");
        }
    }
    
    // Helper method to ensure there is no overlap in tasks executed on the same core.
    private void assertNoOverlap(List<ScheduleEvent> schedule, int numCores) {
        Map<Integer, List<ScheduleEvent>> eventsPerCore = new HashMap<>();
        for (ScheduleEvent event : schedule) {
            eventsPerCore.computeIfAbsent(event.coreId, k -> new ArrayList<>()).add(event);
        }
        for (Map.Entry<Integer, List<ScheduleEvent>> entry : eventsPerCore.entrySet()) {
            List<ScheduleEvent> coreEvents = entry.getValue();
            coreEvents.sort(Comparator.comparingInt(e -> e.startTime));
            for (int i = 1; i < coreEvents.size(); i++) {
                ScheduleEvent prev = coreEvents.get(i - 1);
                ScheduleEvent curr = coreEvents.get(i);
                assertTrue(prev.endTime <= curr.startTime,
                    "Overlap detected on core " + entry.getKey());
            }
        }
    }
    
    // Helper method to check that dependency constraints are satisfied in the schedule.
    private void assertDependencyOrder(List<Task> tasks, List<ScheduleEvent> schedule) {
        Map<Integer, ScheduleEvent> eventMap = new HashMap<>();
        for (ScheduleEvent event : schedule) {
            eventMap.put(event.taskId, event);
        }
        for (Task task : tasks) {
            ScheduleEvent currentEvent = eventMap.get(task.id);
            for (Integer dep : task.dependencies) {
                ScheduleEvent depEvent = eventMap.get(dep);
                assertNotNull(depEvent, "Missing schedule event for dependency task " + dep);
                assertTrue(depEvent.endTime <= currentEvent.startTime,
                    "Task " + task.id + " starts before its dependency " + dep + " finishes");
            }
        }
    }
    
    // Helper method to check that each task meets its deadline.
    private void assertDeadlines(List<Task> tasks, List<ScheduleEvent> schedule) {
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.id, task);
        }
        for (ScheduleEvent event : schedule) {
            Task task = taskMap.get(event.taskId);
            assertNotNull(task, "Task not found for event: " + event.taskId);
            assertTrue(event.endTime <= task.deadline,
                "Task " + task.id + " exceeded its deadline");
        }
    }
    
    @Test
    public void testSimpleFeasibleSchedule() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 10, 50, new ArrayList<>()));
        tasks.add(new Task(2, 15, 60, new ArrayList<>()));
        tasks.add(new Task(3, 8, 40, new ArrayList<>()));
        tasks.add(new Task(4, 12, 70, new ArrayList<>()));
        
        int numCores = 2;
        List<ScheduleEvent> schedule = TaskScheduler.scheduleTasks(tasks, numCores);
        
        assertNotNull(schedule, "Expected a feasible schedule");
        assertSortedByStartTime(schedule);
        assertNoOverlap(schedule, numCores);
        assertDeadlines(tasks, schedule);
    }
    
    @Test
    public void testDependencyEnforcement() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 10, 50, new ArrayList<>()));
        tasks.add(new Task(2, 15, 70, Arrays.asList(1))); // Task 2 depends on Task 1
        tasks.add(new Task(3, 8, 40, new ArrayList<>()));
        tasks.add(new Task(4, 12, 90, Arrays.asList(2, 3))); // Task 4 depends on Task 2 and Task 3
        
        int numCores = 2;
        List<ScheduleEvent> schedule = TaskScheduler.scheduleTasks(tasks, numCores);
        
        assertNotNull(schedule, "Expected a feasible schedule with dependencies satisfied");
        assertDependencyOrder(tasks, schedule);
        assertNoOverlap(schedule, numCores);
        assertDeadlines(tasks, schedule);
    }
    
    @Test
    public void testInfeasibleSchedule() {
        List<Task> tasks = new ArrayList<>();
        // Construct tasks with tight deadlines such that scheduling is impossible.
        tasks.add(new Task(1, 30, 30, new ArrayList<>()));
        tasks.add(new Task(2, 30, 30, Arrays.asList(1)));
        
        int numCores = 1;
        List<ScheduleEvent> schedule = TaskScheduler.scheduleTasks(tasks, numCores);
        
        assertNull(schedule, "The schedule should be infeasible due to deadline constraints");
    }
    
    @Test
    public void testMultipleCoresUtilization() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 20, 100, new ArrayList<>()));
        tasks.add(new Task(2, 25, 120, new ArrayList<>()));
        tasks.add(new Task(3, 15, 90, new ArrayList<>()));
        tasks.add(new Task(4, 10, 80, new ArrayList<>()));
        tasks.add(new Task(5, 30, 150, new ArrayList<>()));
        
        int numCores = 3;
        List<ScheduleEvent> schedule = TaskScheduler.scheduleTasks(tasks, numCores);

        assertNotNull(schedule, "Expected a feasible schedule with multiple cores");
        assertSortedByStartTime(schedule);
        assertNoOverlap(schedule, numCores);
        assertDeadlines(tasks, schedule);
        
        int totalDuration = tasks.stream().mapToInt(task -> task.duration).sum();
        int makespan = schedule.stream().mapToInt(event -> event.endTime).max().orElse(0);
        double utilization = (double) totalDuration / (makespan * numCores);
        assertTrue(utilization > 0, "Resource utilization should be greater than 0");
    }
    
    @Test
    public void testComplexDependencyChain() {
        // Create a chain of dependent tasks.
        List<Task> tasks = new ArrayList<>();
        int numTasks = 10;
        for (int i = 1; i <= numTasks; i++) {
            List<Integer> deps = new ArrayList<>();
            if (i > 1) {
                deps.add(i - 1);
            }
            tasks.add(new Task(i, 10, 100 + i * 10, deps));
        }
        
        int numCores = 2;
        List<ScheduleEvent> schedule = TaskScheduler.scheduleTasks(tasks, numCores);
        
        assertNotNull(schedule, "Expected a feasible schedule for a chain of dependencies");
        assertDependencyOrder(tasks, schedule);
        assertNoOverlap(schedule, numCores);
        assertDeadlines(tasks, schedule);
    }
}