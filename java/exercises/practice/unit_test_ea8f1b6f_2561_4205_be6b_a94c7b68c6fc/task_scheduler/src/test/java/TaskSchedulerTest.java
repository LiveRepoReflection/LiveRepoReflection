import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setup() {
        scheduler = new TaskScheduler();
    }

    // Helper method to collect all tasks from the schedule map
    private Set<Integer> collectScheduledTaskIds(Map<Integer, List<Task>> schedule) {
        Set<Integer> taskIds = new HashSet<>();
        for (List<Task> taskList : schedule.values()) {
            for (Task t : taskList) {
                taskIds.add(t.getTaskId());
            }
        }
        return taskIds;
    }

    // Helper method to verify that if a dependency is scheduled on the same worker, 
    // it appears before its dependent task.
    private void checkDependencyOrder(Map<Integer, List<Task>> schedule) {
        for (Map.Entry<Integer, List<Task>> entry : schedule.entrySet()) {
            List<Task> taskList = entry.getValue();
            Map<Integer, Integer> taskPosition = new HashMap<>();
            for (int i = 0; i < taskList.size(); i++) {
                taskPosition.put(taskList.get(i).getTaskId(), i);
            }
            for (Task t : taskList) {
                for (Integer dep : t.getDependencies()) {
                    if (taskPosition.containsKey(dep)) {
                        int depPos = taskPosition.get(dep);
                        int tPos = taskPosition.get(t.getTaskId());
                        assertTrue(depPos < tPos, "Dependency task " + dep + " should come before task " + t.getTaskId() + " on worker " + entry.getKey());
                    }
                }
            }
        }
    }

    @Test
    public void testBasicScheduling() {
        // Create tasks with dependencies:
        // Task1 has no dependency, Task2 depends on Task1, Task3 depends on Task2
        List<Task> tasks = Arrays.asList(
            new Task(1, 2, 4, 1, Collections.emptyList(), 10),
            new Task(2, 1, 2, 2, Arrays.asList(1), 5),
            new Task(3, 3, 1, 1, Arrays.asList(2), 8)
        );

        // Create two workers with different resource capacities.
        List<Worker> workers = Arrays.asList(
            new Worker(1, 4, 8, 4),
            new Worker(2, 2, 4, 2)
        );

        Map<Integer, List<Task>> schedule = scheduler.schedule(tasks, workers);
        // A feasible schedule should schedule all tasks.
        Set<Integer> scheduledTaskIds = collectScheduledTaskIds(schedule);
        assertEquals(3, scheduledTaskIds.size(), "All tasks should be scheduled");
        // Verify dependency order within same worker if applicable.
        checkDependencyOrder(schedule);
    }

    @Test
    public void testFeasibilityFailureDueToResources() {
        // Create a task that requires more resources than any worker can provide.
        List<Task> tasks = Arrays.asList(
            new Task(1, 10, 10, 10, Collections.emptyList(), 15)
        );
        // Create a worker that cannot fulfill the task resource requirements.
        List<Worker> workers = Arrays.asList(
            new Worker(1, 5, 5, 5)
        );
        Map<Integer, List<Task>> schedule = scheduler.schedule(tasks, workers);
        // Expect an empty schedule as the task cannot be scheduled.
        assertTrue(schedule.isEmpty(), "Schedule should be empty when task requirements exceed worker capacities");
    }

    @Test
    public void testParallelSchedulingWithIndependentTasks() {
        // All tasks are independent. They should be distributed across available workers.
        List<Task> tasks = Arrays.asList(
            new Task(1, 2, 2, 1, Collections.emptyList(), 10),
            new Task(2, 1, 1, 1, Collections.emptyList(), 8),
            new Task(3, 2, 3, 2, Collections.emptyList(), 12),
            new Task(4, 1, 2, 1, Collections.emptyList(), 7)
        );
        // Create three workers.
        List<Worker> workers = Arrays.asList(
            new Worker(1, 3, 4, 2),
            new Worker(2, 3, 4, 2),
            new Worker(3, 3, 4, 2)
        );
        Map<Integer, List<Task>> schedule = scheduler.schedule(tasks, workers);
        // All tasks should be scheduled.
        Set<Integer> scheduledTaskIds = collectScheduledTaskIds(schedule);
        assertEquals(4, scheduledTaskIds.size(), "All independent tasks should be scheduled");
    }

    @Test
    public void testComplexDependenciesAndTieBreaking() {
        // Create tasks with varying execution times and dependencies to test tie-breaking.
        List<Task> tasks = new ArrayList<>();
        // Task 1: No dependency, long execution time.
        tasks.add(new Task(1, 2, 2, 1, Collections.emptyList(), 15));
        // Task 2: Depends on Task 1.
        tasks.add(new Task(2, 1, 1, 1, Arrays.asList(1), 15));
        // Task 3: No dependency, same execution time as Task 1 but more dependencies later.
        tasks.add(new Task(3, 2, 2, 1, Collections.emptyList(), 15));
        // Task 4: Depends on Task 3.
        tasks.add(new Task(4, 1, 2, 1, Arrays.asList(3), 5));
        // Task 5: Depends on Task 2 and Task 4, shorter execution time.
        tasks.add(new Task(5, 1, 1, 1, Arrays.asList(2, 4), 8));

        // Create workers with sufficient resources.
        List<Worker> workers = Arrays.asList(
            new Worker(1, 4, 6, 3),
            new Worker(2, 4, 6, 3)
        );

        Map<Integer, List<Task>> schedule = scheduler.schedule(tasks, workers);
        // All tasks should be scheduled.
        Set<Integer> scheduledTaskIds = collectScheduledTaskIds(schedule);
        assertEquals(5, scheduledTaskIds.size(), "All tasks with dependencies should be scheduled");
        // Check dependency order within same worker.
        checkDependencyOrder(schedule);

        // Additional check: tasks with longer execution time should be scheduled earlier in a worker if possible.
        // For each worker, if two tasks have equal exec time, the one with more dependencies (later tasks are dependent) should come first.
        for (List<Task> taskList : schedule.values()) {
            for (int i = 0; i < taskList.size() - 1; i++) {
                Task current = taskList.get(i);
                Task next = taskList.get(i + 1);
                if (current.getEstimatedExecutionTime() == next.getEstimatedExecutionTime()) {
                    // Count of dependencies can be used as a tie-break criteria.
                    int currentDepCount = current.getDependencies().size();
                    int nextDepCount = next.getDependencies().size();
                    // In our tie breaking, task with more dependencies should be prioritized (appear earlier)
                    assertTrue(currentDepCount >= nextDepCount, "Tie-breaking by dependency count failed on worker list ordering");
                }
            }
        }
    }

    @Test
    public void testEmptyTaskList() {
        // When no tasks are provided, the scheduler should return an empty schedule.
        List<Task> tasks = new ArrayList<>();
        List<Worker> workers = Arrays.asList(
            new Worker(1, 4, 4, 2),
            new Worker(2, 3, 3, 2)
        );
        Map<Integer, List<Task>> schedule = scheduler.schedule(tasks, workers);
        assertTrue(schedule.isEmpty() || collectScheduledTaskIds(schedule).isEmpty(), "Empty task list should result in an empty schedule");
    }
}