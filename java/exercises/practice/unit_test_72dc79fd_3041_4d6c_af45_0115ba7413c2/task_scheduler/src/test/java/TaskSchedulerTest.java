import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TaskSchedulerTest {

    // Helper method to create a task with given id, duration, deadline and dependencies.
    private Task createTask(int id, int duration, int deadline, List<Integer> dependencies) {
        return new Task(id, duration, deadline, dependencies);
    }

    @Test
    public void testNoTasks() {
        List<Task> tasks = new ArrayList<>();
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(0, result, "Empty task list should have 0 total lateness");
    }

    @Test
    public void testSingleTaskOnTime() {
        List<Task> tasks = Arrays.asList(
            createTask(1, 5, 10, Collections.emptyList())
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(0, result, "Single task finishing on time should have 0 lateness");
    }

    @Test
    public void testSingleTaskLate() {
        List<Task> tasks = Arrays.asList(
            createTask(1, 15, 10, Collections.emptyList())
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(5, result, "Single task finishing late should have lateness equal to finishing time minus deadline");
    }

    @Test
    public void testMultipleIndependentTasks() {
        // Tasks with no dependencies can be optimally scheduled.
        // Task 1: duration=5, deadline=10
        // Task 2: duration=3, deadline=12
        // Task 3: duration=7, deadline=20
        List<Task> tasks = Arrays.asList(
            createTask(1, 5, 10, Collections.emptyList()),
            createTask(2, 3, 12, Collections.emptyList()),
            createTask(3, 7, 20, Collections.emptyList())
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        // One optimal schedule is: Task1 (0-5), Task2 (5-8), Task3 (8-15) yielding no lateness.
        assertEquals(0, result, "Optimal schedule with independent tasks should yield minimal total lateness");
    }

    @Test
    public void testTasksWithDependenciesNoLate() {
        // Example from problem description:
        // Task 1: duration=5, deadline=10, dependencies=[]
        // Task 2: duration=3, deadline=12, dependencies=[1]
        // Task 3: duration=7, deadline=20, dependencies=[1,2]
        // Task 4: duration=2, deadline=15, dependencies=[]
        List<Task> tasks = Arrays.asList(
            createTask(1, 5, 10, Collections.emptyList()),
            createTask(2, 3, 12, Arrays.asList(1)),
            createTask(3, 7, 20, Arrays.asList(1, 2)),
            createTask(4, 2, 15, Collections.emptyList())
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(0, result, "All tasks should be scheduled to finish on or before their deadlines");
    }

    @Test
    public void testTasksWithDependenciesAndLate() {
        // Scenario where deadlines are tight.
        // Task 1: duration=5, deadline=4, dependencies=[]
        // Task 2: duration=3, deadline=6, dependencies=[1]
        // Task 3: duration=7, deadline=8, dependencies=[1]
        // A possible schedule: Task1 (0-5), Task2 (5-8), Task3 (8-15)
        // Latenesses: Task1: 1, Task2: 2, Task3: 7, total lateness = 10.
        List<Task> tasks = Arrays.asList(
            createTask(1, 5, 4, Collections.emptyList()),
            createTask(2, 3, 6, Arrays.asList(1)),
            createTask(3, 7, 8, Arrays.asList(1))
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(10, result, "Total lateness should match the computed optimal lateness");
    }

    @Test
    public void testComplexDependencyGraph() {
        // A more complex dependency graph scenario:
        // Task 1: duration=4, deadline=6, dependencies=[]
        // Task 2: duration=2, deadline=8, dependencies=[1]
        // Task 3: duration=3, deadline=10, dependencies=[1]
        // Task 4: duration=5, deadline=15, dependencies=[2, 3]
        // Task 5: duration=1, deadline=7, dependencies=[1]
        // Task 6: duration=2, deadline=12, dependencies=[5]
        // One possible optimal schedule:
        // Task1 (0-4): lateness 0
        // Task5 (4-5): lateness 0
        // Task2 (5-7): lateness 0
        // Task3 (7-10): lateness 0
        // Task6 (10-12): lateness 0
        // Task4 (12-17): lateness 2 (17-15)
        List<Task> tasks = Arrays.asList(
            createTask(1, 4, 6, Collections.emptyList()),
            createTask(2, 2, 8, Arrays.asList(1)),
            createTask(3, 3, 10, Arrays.asList(1)),
            createTask(4, 5, 15, Arrays.asList(2, 3)),
            createTask(5, 1, 7, Arrays.asList(1)),
            createTask(6, 2, 12, Arrays.asList(5))
        );
        int result = TaskScheduler.minTotalLateness(tasks);
        assertEquals(2, result, "The minimal total lateness in the complex graph should be correctly computed");
    }
}