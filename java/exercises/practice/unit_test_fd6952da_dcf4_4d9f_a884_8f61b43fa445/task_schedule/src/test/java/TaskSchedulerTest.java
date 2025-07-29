import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import task_schedule.Task;
import task_schedule.TaskScheduler;

public class TaskSchedulerTest {

    @Test
    public void testSingleTask() {
        List<Task> tasks = new ArrayList<>();
        // Task(id, duration, deadline, dependencies)
        tasks.add(new Task(0, 5, 10, Collections.emptyList()));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // A single task can always be delayed so that it finishes exactly at its deadline.
        assertEquals(0, result);
    }

    @Test
    public void testLinearDependencies() {
        List<Task> tasks = new ArrayList<>();
        // Two tasks in a chain: Task 1 depends on Task 0.
        tasks.add(new Task(0, 3, 5, Collections.emptyList()));
        tasks.add(new Task(1, 4, 11, Arrays.asList(0)));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // It is possible to schedule these tasks so that each finishes by its deadline.
        assertEquals(0, result);
    }

    @Test
    public void testInsufficientSlack() {
        List<Task> tasks = new ArrayList<>();
        // A dependency chain where deadlines are too tight.
        tasks.add(new Task(0, 5, 6, Collections.emptyList()));
        tasks.add(new Task(1, 4, 8, Arrays.asList(0)));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // Even with optimal delays, the dependent task will finish 2 time units late.
        assertEquals(2, result);
    }

    @Test
    public void testParallelTasks() {
        List<Task> tasks = new ArrayList<>();
        // Two independent tasks that can be executed in parallel.
        tasks.add(new Task(0, 4, 5, Collections.emptyList()));
        tasks.add(new Task(1, 6, 8, Collections.emptyList()));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // Both tasks can be delayed to finish exactly at their deadlines.
        assertEquals(0, result);
    }

    @Test
    public void testComplexGraph() {
        List<Task> tasks = new ArrayList<>();
        // A more intricate dependency graph.
        tasks.add(new Task(0, 5, 10, Collections.emptyList()));
        tasks.add(new Task(1, 3, 15, Arrays.asList(0)));
        tasks.add(new Task(2, 7, 20, Arrays.asList(1)));
        tasks.add(new Task(3, 2, 12, Arrays.asList(0)));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // With optimal scheduling, tasks can meet their deadlines.
        assertEquals(0, result);
    }

    @Test
    public void testImpossibleSchedule() {
        List<Task> tasks = new ArrayList<>();
        // A task whose duration is longer than its deadline makes scheduling impossible.
        tasks.add(new Task(0, 20, 10, Collections.emptyList()));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // Indicate failure since it is impossible to finish before the deadline.
        assertEquals(Integer.MAX_VALUE, result);
    }

    @Test
    public void testMultipleDependencies() {
        List<Task> tasks = new ArrayList<>();
        // A task with multiple dependencies.
        tasks.add(new Task(0, 3, 10, Collections.emptyList()));
        tasks.add(new Task(1, 2, 8, Collections.emptyList()));
        tasks.add(new Task(2, 4, 15, Arrays.asList(0, 1)));
        tasks.add(new Task(3, 1, 12, Arrays.asList(0)));
        tasks.add(new Task(4, 2, 20, Arrays.asList(2, 3)));
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.minimizeMaximumLateness(tasks);
        // Optimal scheduling should allow all tasks to meet their deadlines.
        assertEquals(0, result);
    }
}