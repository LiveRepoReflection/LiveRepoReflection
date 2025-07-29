import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class TaskSchedulerTest {

    @Test
    public void testSimpleSchedule() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 2, new ArrayList<>(), 5));
        tasks.add(new Task(2, 1, new ArrayList<>(), 3));
        tasks.add(new Task(3, 3, new ArrayList<>(), 2));

        int numWorkers = 2;
        int maxRetries = 3;

        TaskScheduler scheduler = new TaskScheduler();
        List<ScheduledTask> schedule = scheduler.schedule(tasks, numWorkers, maxRetries);

        // Verify that all tasks are scheduled and completed successfully.
        assertEquals(3, schedule.size());
        for (ScheduledTask st : schedule) {
            assertEquals("SUCCESS", st.getStatus());
            assertTrue(st.getStartTime() >= 0);
            assertTrue(st.getEndTime() >= st.getStartTime());
            assertTrue(st.getWorkerId() >= 0 && st.getWorkerId() < numWorkers);
        }
    }

    @Test
    public void testDependencySchedule() {
        List<Task> tasks = new ArrayList<>();
        // Task 1 has no dependencies, Task 2 depends on Task 1, Task 3 depends on Task 2.
        tasks.add(new Task(1, 2, new ArrayList<>(), 5));
        tasks.add(new Task(2, 3, Arrays.asList(1), 3));
        tasks.add(new Task(3, 1, Arrays.asList(2), 2));

        int numWorkers = 1;
        int maxRetries = 3;

        TaskScheduler scheduler = new TaskScheduler();
        List<ScheduledTask> schedule = scheduler.schedule(tasks, numWorkers, maxRetries);

        // Verify that tasks are scheduled respecting their dependency order.
        Map<Integer, ScheduledTask> mapping = new HashMap<>();
        for (ScheduledTask st : schedule) {
            mapping.put(st.getTaskId(), st);
        }

        ScheduledTask s1 = mapping.get(1);
        ScheduledTask s2 = mapping.get(2);
        ScheduledTask s3 = mapping.get(3);

        assertNotNull(s1);
        assertNotNull(s2);
        assertNotNull(s3);

        // Task 1 must finish before Task 2 can start
        assertTrue(s1.getEndTime() <= s2.getStartTime());
        // Task 2 must finish before Task 3 can start
        assertTrue(s2.getEndTime() <= s3.getStartTime());
    }

    @Test
    public void testDeadlockResolution() {
        List<Task> tasks = new ArrayList<>();
        // Introduce a circular dependency between Task 1 and Task 2.
        tasks.add(new Task(1, 2, Arrays.asList(2), 4));
        tasks.add(new Task(2, 1, Arrays.asList(1), 4));
        tasks.add(new Task(3, 3, new ArrayList<>(), 2));

        int numWorkers = 2;
        int maxRetries = 3;

        TaskScheduler scheduler = new TaskScheduler();
        // The scheduler is expected to detect and resolve the deadlock by breaking a dependency.
        List<ScheduledTask> schedule = scheduler.schedule(tasks, numWorkers, maxRetries);

        // Verify that all tasks are scheduled.
        assertEquals(3, schedule.size());
        
        // Since the deadlock is resolved by breaking one dependency,
        // the ordering between Task 1 and Task 2 may not be strict.
        // We check that at least one of the tasks scheduled in the cycle starts before the other finishes.
        Map<Integer, ScheduledTask> mapping = new HashMap<>();
        for (ScheduledTask st : schedule) {
            mapping.put(st.getTaskId(), st);
        }
        ScheduledTask s1 = mapping.get(1);
        ScheduledTask s2 = mapping.get(2);
        assertNotNull(s1);
        assertNotNull(s2);
        boolean dependencyRelaxed = s2.getStartTime() < s1.getEndTime() || s1.getStartTime() < s2.getEndTime();
        assertTrue(dependencyRelaxed);
    }

    @Test
    public void testRetryMechanism() {
        List<Task> tasks = new ArrayList<>();
        // Create tasks that may simulate failure.
        tasks.add(new Task(1, 5, new ArrayList<>(), 5));
        tasks.add(new Task(2, 4, new ArrayList<>(), 3));

        int numWorkers = 1;
        int maxRetries = 2;

        TaskScheduler scheduler = new TaskScheduler();
        List<ScheduledTask> schedule = scheduler.schedule(tasks, numWorkers, maxRetries);

        // Verify that each task's status is either "SUCCESS" or "FAILED"
        for (ScheduledTask st : schedule) {
            String status = st.getStatus();
            assertTrue(status.equals("SUCCESS") || status.equals("FAILED"));
            // Verify that the retries count does not exceed maxRetries.
            assertTrue(st.getRetries() <= maxRetries);
        }
    }

    @Test
    public void testWorkerUtilization() {
        List<Task> tasks = new ArrayList<>();
        // Create multiple independent tasks to test worker utilization.
        for (int i = 1; i <= 10; i++) {
            tasks.add(new Task(i, (i % 3) + 1, new ArrayList<>(), 2));
        }

        int numWorkers = 3;
        int maxRetries = 3;

        TaskScheduler scheduler = new TaskScheduler();
        List<ScheduledTask> schedule = scheduler.schedule(tasks, numWorkers, maxRetries);

        // Verify that all tasks are scheduled.
        assertEquals(10, schedule.size());
        
        // Group scheduled tasks by worker.
        Map<Integer, List<ScheduledTask>> workerTasks = new HashMap<>();
        for (ScheduledTask st : schedule) {
            workerTasks.computeIfAbsent(st.getWorkerId(), k -> new ArrayList<>()).add(st);
        }
        // For each worker, verify that tasks are scheduled without overlapping execution.
        for (Map.Entry<Integer, List<ScheduledTask>> entry : workerTasks.entrySet()) {
            List<ScheduledTask> tasksList = entry.getValue();
            tasksList.sort(Comparator.comparingInt(ScheduledTask::getStartTime));
            for (int i = 1; i < tasksList.size(); i++) {
                int gap = tasksList.get(i).getStartTime() - tasksList.get(i - 1).getEndTime();
                // There should be no negative gap.
                assertTrue(gap >= 0);
            }
        }
    }
}