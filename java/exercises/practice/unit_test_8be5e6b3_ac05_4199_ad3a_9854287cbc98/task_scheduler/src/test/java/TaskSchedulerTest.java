import org.junit.Test;
import org.junit.Before;
import org.junit.Rule;
import org.junit.rules.ExpectedException;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.*;

public class TaskSchedulerTest {

    // A simple Task representation for testing purposes.
    static class Task {
        int id;
        int processingTime;
        int deadline;
        List<Integer> dependencies;

        Task(int id, int processingTime, int deadline, List<Integer> dependencies) {
            this.id = id;
            this.processingTime = processingTime;
            this.deadline = deadline;
            this.dependencies = new ArrayList<>(dependencies);
        }
    }

    // Assume that TaskScheduler is the class containing the scheduleTasks method.
    // The scheduleTasks method is defined as:
    // public static List<Integer> scheduleTasks(List<Task> tasks, List<Integer> cancelledTaskIds)
    // and may throw an IllegalArgumentException if circular dependencies are detected.
    
    // Helper method to validate that the returned order is topologically valid, i.e.,
    // all dependencies of a task appear before the task in the order.
    private boolean isValidOrder(List<Task> tasks, List<Integer> schedule) {
        // Map task id to Task for easy lookup.
        java.util.Map<Integer, Task> taskMap = new java.util.HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.id, t);
        }
        // Set to keep track of tasks seen so far in the schedule.
        java.util.Set<Integer> seen = new java.util.HashSet<>();
        for (int id : schedule) {
            Task t = taskMap.get(id);
            if (t == null) {
                // Unknown task in output.
                return false;
            }
            // Check all dependencies exist in seen.
            for (int dep : t.dependencies) {
                if (!seen.contains(dep)) {
                    return false;
                }
            }
            seen.add(id);
        }
        // All tasks scheduled? (Note: cancelled tasks may be absent.)
        // This check is not mandatory because scheduling may drop tasks if cancelled.
        return true;
    }

    // Rule to test exception messages and types.
    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Test
    public void testEmptyTasks() {
        List<Task> tasks = new ArrayList<>();
        List<Integer> cancelled = new ArrayList<>();
        List<Integer> result = TaskScheduler.scheduleTasks(tasks, cancelled);
        assertNotNull(result);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testSimpleSchedule() {
        // Task definitions:
        // Task 1: No dependencies, time=2, deadline=5
        // Task 2: Depends on 1, time=3, deadline=7
        // Task 3: Depends on 1, time=1, deadline=4
        // Task 4: Depends on 2 and 3, time=4, deadline=9
        Task t1 = new Task(1, 2, 5, Collections.emptyList());
        Task t2 = new Task(2, 3, 7, Arrays.asList(1));
        Task t3 = new Task(3, 1, 4, Arrays.asList(1));
        Task t4 = new Task(4, 4, 9, Arrays.asList(2, 3));
        List<Task> tasks = Arrays.asList(t1, t2, t3, t4);
        List<Integer> cancelled = new ArrayList<>();

        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks, cancelled);
        // Validate that the schedule respects dependency ordering.
        assertTrue(isValidOrder(tasks, schedule));

        // Additionally, all tasks should be scheduled.
        assertEquals(4, schedule.size());
        // Check that all task ids are present.
        assertTrue(schedule.containsAll(Arrays.asList(1, 2, 3, 4)));
    }

    @Test
    public void testCancellationPropagation() {
        // Create tasks with a dependency chain.
        // 1 -> 2 -> 3, 4 independent.
        Task t1 = new Task(1, 2, 5, Collections.emptyList());
        Task t2 = new Task(2, 3, 7, Arrays.asList(1));
        Task t3 = new Task(3, 1, 4, Arrays.asList(2));
        Task t4 = new Task(4, 4, 9, Collections.emptyList());
        List<Task> tasks = Arrays.asList(t1, t2, t3, t4);

        // Cancel task 2 and expect task 3 to be cancelled due to dependency.
        List<Integer> cancelled = Arrays.asList(2);
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks, cancelled);

        // Validate that cancelled tasks do not appear in the schedule.
        assertFalse(schedule.contains(2));
        assertFalse(schedule.contains(3));

        // Tasks 1 and 4 should still be scheduled.
        assertTrue(schedule.contains(1));
        assertTrue(schedule.contains(4));

        // Validate dependency ordering for remaining tasks.
        List<Task> remainingTasks = new ArrayList<>();
        for (Task t : tasks) {
            if (!cancelled.contains(t.id) && t.id != 3) {  // t3 is implicitly cancelled
                remainingTasks.add(t);
            }
        }
        assertTrue(isValidOrder(remainingTasks, schedule));
    }

    @Test
    public void testCircularDependencyDetection() {
        // Create tasks with a circular dependency:
        // 1 -> 2, 2 -> 3, 3 -> 1.
        Task t1 = new Task(1, 2, 5, Arrays.asList(3));
        Task t2 = new Task(2, 3, 7, Arrays.asList(1));
        Task t3 = new Task(3, 1, 4, Arrays.asList(2));
        List<Task> tasks = Arrays.asList(t1, t2, t3);
        List<Integer> cancelled = new ArrayList<>();

        // Expect an IllegalArgumentException to be thrown.
        thrown.expect(IllegalArgumentException.class);
        thrown.expectMessage("circular dependencies");
        TaskScheduler.scheduleTasks(tasks, cancelled);
    }

    @Test
    public void testComplexScheduleOptimization() {
        // Construct a more complex scenario with multiple tasks and interwoven dependencies.
        Task t1 = new Task(1, 4, 10, Collections.emptyList());
        Task t2 = new Task(2, 2, 8, Arrays.asList(1));
        Task t3 = new Task(3, 3, 12, Arrays.asList(1));
        Task t4 = new Task(4, 1, 7, Arrays.asList(2, 3));
        Task t5 = new Task(5, 5, 15, Arrays.asList(2));
        Task t6 = new Task(6, 2, 9, Arrays.asList(3));
        Task t7 = new Task(7, 3, 20, Arrays.asList(4, 5, 6));
        List<Task> tasks = Arrays.asList(t1, t2, t3, t4, t5, t6, t7);
        List<Integer> cancelled = new ArrayList<>();

        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks, cancelled);
        // Validate topological order.
        assertTrue(isValidOrder(tasks, schedule));

        // All tasks should be scheduled.
        assertEquals(7, schedule.size());
        assertTrue(schedule.containsAll(Arrays.asList(1,2,3,4,5,6,7)));
    }
}