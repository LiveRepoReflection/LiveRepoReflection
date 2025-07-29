import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class TaskSchedulerTest {

    @Test
    public void testEmptyTasksAndMachines() {
        List<Task> tasks = new ArrayList<>();
        List<Machine> machines = new ArrayList<>();

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        assertEquals(0, makespan, "No tasks and no machines should result in a makespan of 0.");
    }

    @Test
    public void testEmptyTasksNonEmptyMachines() {
        List<Task> tasks = new ArrayList<>();
        List<Machine> machines = Arrays.asList(
            new Machine("M1", 4, 16),
            new Machine("M2", 8, 32)
        );

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        assertEquals(0, makespan, "No tasks should result in a makespan of 0.");
    }

    @Test
    public void testSingleTaskNoDependencies() {
        Task task = new Task("T1", 2, 4, 10, new HashSet<>());
        List<Task> tasks = Arrays.asList(task);
        List<Machine> machines = Arrays.asList(new Machine("M1", 4, 16));

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        assertEquals(10, makespan, "A single task should complete in its execution time.");
    }

    @Test
    public void testMultipleTasksNoDependencies() {
        // Three independent tasks that can run concurrently given ample resources.
        Task task1 = new Task("T1", 2, 4, 10, new HashSet<>());
        Task task2 = new Task("T2", 2, 4, 15, new HashSet<>());
        Task task3 = new Task("T3", 2, 4, 5, new HashSet<>());
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        List<Machine> machines = Arrays.asList(
            new Machine("M1", 4, 16),
            new Machine("M2", 4, 16)
        );

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        // Expected makespan is the maximum execution time (15) if tasks are run concurrently.
        assertEquals(15, makespan, "Concurrent tasks should result in the maximum individual execution time as the makespan.");
    }

    @Test
    public void testTasksWithDependencies() {
        // Chain dependencies: T1 -> T2 -> T3 (T2 depends on T1, T3 depends on T2)
        Task task1 = new Task("T1", 2, 4, 10, new HashSet<>());
        Task task2 = new Task("T2", 2, 4, 15, new HashSet<>(Arrays.asList("T1")));
        Task task3 = new Task("T3", 2, 4, 5, new HashSet<>(Arrays.asList("T2")));
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        List<Machine> machines = Arrays.asList(new Machine("M1", 4, 16));

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        // Sequential execution due to dependencies: total time = 10 + 15 + 5 = 30.
        assertEquals(30, makespan, "Dependent tasks must run sequentially resulting in the summed execution time.");
    }

    @Test
    public void testMultipleSchedulingOptions() {
        // T1 and T2 can run concurrently, and T3 depends on both T1 and T2.
        Task task1 = new Task("T1", 2, 4, 10, new HashSet<>());
        Task task2 = new Task("T2", 2, 4, 12, new HashSet<>());
        Task task3 = new Task("T3", 2, 4, 8, new HashSet<>(Arrays.asList("T1", "T2")));
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        List<Machine> machines = Arrays.asList(
            new Machine("M1", 4, 16),
            new Machine("M2", 4, 16)
        );

        TaskScheduler scheduler = new TaskScheduler();
        int makespan = scheduler.schedule(tasks, machines);
        // T1 and T2 run concurrently, so the max time is 12, then T3 takes 8, total = 20.
        assertEquals(20, makespan, "Tasks with partial parallelism should yield an optimized makespan.");
    }

    @Test
    public void testCycleDetection() {
        // Create cyclic dependency: T1 -> T2 and T2 -> T1.
        Task task1 = new Task("T1", 2, 4, 10, new HashSet<>(Arrays.asList("T2")));
        Task task2 = new Task("T2", 2, 4, 15, new HashSet<>(Arrays.asList("T1")));
        List<Task> tasks = Arrays.asList(task1, task2);
        List<Machine> machines = Arrays.asList(new Machine("M1", 4, 16));

        TaskScheduler scheduler = new TaskScheduler();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            scheduler.schedule(tasks, machines);
        });
        String expectedMessage = "cyclic dependency";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.toLowerCase().contains(expectedMessage), "A cyclic dependency should be detected.");
    }

    @Test
    public void testInsufficientResources() {
        // Task that requires more CPU cores than any available machine can provide.
        Task task = new Task("T1", 10, 4, 10, new HashSet<>());
        List<Task> tasks = Arrays.asList(task);
        List<Machine> machines = Arrays.asList(
            new Machine("M1", 4, 16),
            new Machine("M2", 4, 16)
        );

        TaskScheduler scheduler = new TaskScheduler();
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            scheduler.schedule(tasks, machines);
        });
        String expectedMessage = "insufficient resources";
        String actualMessage = exception.getMessage();
        assertTrue(actualMessage.toLowerCase().contains(expectedMessage), "The scheduler should flag tasks with resource requirements exceeding machine capacity.");
    }
}