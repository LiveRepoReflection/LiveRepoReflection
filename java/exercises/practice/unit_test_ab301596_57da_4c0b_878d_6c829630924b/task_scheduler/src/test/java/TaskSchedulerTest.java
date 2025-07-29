import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class TaskSchedulerTest {

    @Test
    public void testNoDependenciesBasicSchedule() {
        Task task1 = new Task(1, 3, 10, List.of());
        Task task2 = new Task(2, 2, 8, List.of());
        List<Task> tasks = Arrays.asList(task1, task2);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertEquals(Arrays.asList(2, 1), result);
    }

    @Test
    public void testWithDependencies() {
        Task task1 = new Task(1, 5, 10, List.of());
        Task task2 = new Task(2, 3, 15, List.of(1));
        Task task3 = new Task(3, 2, 12, List.of(1));
        Task task4 = new Task(4, 4, 20, List.of(2, 3));
        List<Task> tasks = Arrays.asList(task1, task2, task3, task4);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertTrue(result.equals(Arrays.asList(1, 2, 3, 4)) || 
                 result.equals(Arrays.asList(1, 3, 2, 4)));
    }

    @Test
    public void testImpossibleDeadline() {
        Task task1 = new Task(1, 5, 4, List.of());
        Task task2 = new Task(2, 3, 8, List.of(1));
        List<Task> tasks = Arrays.asList(task1, task2);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testCyclicDependencies() {
        Task task1 = new Task(1, 2, 10, List.of(2));
        Task task2 = new Task(2, 3, 15, List.of(1));
        List<Task> tasks = Arrays.asList(task1, task2);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testLargeNumberOfTasks() {
        List<Task> tasks = List.of(
            new Task(1, 1, 1000, List.of()),
            new Task(2, 1, 1000, List.of(1)),
            new Task(3, 1, 1000, List.of(2)),
            new Task(4, 1, 1000, List.of(3)),
            new Task(5, 1, 1000, List.of(4))
        );
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertEquals(Arrays.asList(1, 2, 3, 4, 5), result);
    }

    @Test
    public void testEmptyInput() {
        List<Task> tasks = List.of();
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertTrue(result.isEmpty());
    }

    @Test
    public void testSingleTask() {
        Task task = new Task(1, 5, 10, List.of());
        List<Task> tasks = List.of(task);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertEquals(List.of(1), result);
    }

    @Test
    public void testComplexDependencies() {
        Task task1 = new Task(1, 2, 20, List.of());
        Task task2 = new Task(2, 3, 15, List.of(1));
        Task task3 = new Task(3, 4, 25, List.of(1));
        Task task4 = new Task(4, 1, 30, List.of(2, 3));
        Task task5 = new Task(5, 5, 35, List.of(4));
        List<Task> tasks = Arrays.asList(task1, task2, task3, task4, task5);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertEquals(Arrays.asList(1, 2, 3, 4, 5), result);
    }

    @Test
    public void testZeroDurationTasks() {
        Task task1 = new Task(1, 0, 10, List.of());
        Task task2 = new Task(2, 0, 10, List.of(1));
        List<Task> tasks = Arrays.asList(task1, task2);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertTrue(result.equals(Arrays.asList(1, 2)) || 
                 result.equals(Arrays.asList(2, 1)));
    }

    @Test
    public void testTightDeadlines() {
        Task task1 = new Task(1, 5, 5, List.of());
        Task task2 = new Task(2, 3, 8, List.of(1));
        Task task3 = new Task(3, 2, 10, List.of(2));
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        
        List<Integer> result = TaskScheduler.scheduleTasks(tasks);
        assertEquals(Arrays.asList(1, 2, 3), result);
    }
}