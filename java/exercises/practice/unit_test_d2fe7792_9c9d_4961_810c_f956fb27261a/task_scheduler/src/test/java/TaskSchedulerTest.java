import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setUp() {
        // Assume maxRetries is set to 3 for testing fault tolerance.
        scheduler = new TaskScheduler(3);
    }

    @Test
    public void testSingleTaskExecution() throws InterruptedException {
        // Register a worker node with sufficient resources.
        WorkerNode worker = new WorkerNode("worker-1", new Resource(4, 4096));
        scheduler.registerWorker(worker);

        // Create a simple task with no dependencies and high priority.
        Task task = new Task("task-1", new Resource(2, 2048), "echo Hello", Collections.emptyList(), 10);
        scheduler.submitTask(task);

        // Execute tasks synchronously in the test.
        scheduler.executeAll();

        // Verify that the task completes successfully.
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("task-1"));
    }

    @Test
    public void testTaskDependencies() throws InterruptedException {
        WorkerNode worker = new WorkerNode("worker-1", new Resource(4, 4096));
        scheduler.registerWorker(worker);

        // Create two tasks where task-2 depends on task-1.
        Task task1 = new Task("task-1", new Resource(1, 1024), "echo Task1", Collections.emptyList(), 5);
        Task task2 = new Task("task-2", new Resource(1, 1024), "echo Task2", Arrays.asList("task-1"), 5);

        scheduler.submitTask(task1);
        scheduler.submitTask(task2);

        scheduler.executeAll();

        // Both tasks should be completed and task-1 should complete before task-2.
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("task-1"));
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("task-2"));
        // Optionally check the scheduling order if the API provides an execution log.
        List<String> executionLog = scheduler.getExecutionLog();
        int indexTask1 = executionLog.indexOf("task-1");
        int indexTask2 = executionLog.indexOf("task-2");
        assertTrue(indexTask1 != -1 && indexTask2 != -1 && indexTask1 < indexTask2);
    }

    @Test
    public void testPriorityScheduling() throws InterruptedException {
        WorkerNode worker = new WorkerNode("worker-1", new Resource(8, 8192));
        scheduler.registerWorker(worker);

        // Create tasks with different priorities.
        Task lowPriorityTask = new Task("low", new Resource(2, 2048), "echo low", Collections.emptyList(), 1);
        Task highPriorityTask = new Task("high", new Resource(2, 2048), "echo high", Collections.emptyList(), 10);
        Task mediumPriorityTask = new Task("medium", new Resource(2, 2048), "echo medium", Collections.emptyList(), 5);

        scheduler.submitTask(lowPriorityTask);
        scheduler.submitTask(highPriorityTask);
        scheduler.submitTask(mediumPriorityTask);

        scheduler.executeAll();

        // Verify that all tasks completed.
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("low"));
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("medium"));
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("high"));

        // Verify scheduling order using execution log.
        List<String> log = scheduler.getExecutionLog();
        int highIndex = log.indexOf("high");
        int mediumIndex = log.indexOf("medium");
        int lowIndex = log.indexOf("low");

        assertTrue(highIndex < mediumIndex);
        assertTrue(mediumIndex < lowIndex);
    }

    @Test
    public void testCircularDependencyDetection() {
        // Create tasks with circular dependency: task-1 depends on task-2, and task-2 depends on task-1.
        Task task1 = new Task("task-1", new Resource(1, 1024), "echo Task1", Arrays.asList("task-2"), 5);
        Task task2 = new Task("task-2", new Resource(1, 1024), "echo Task2", Arrays.asList("task-1"), 5);

        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            scheduler.submitTask(task1);
            scheduler.submitTask(task2);
            // When execution is triggered, the scheduler should detect the circular dependency.
            scheduler.executeAll();
        });
        String expectedMessage = "Circular dependency detected";
        assertTrue(exception.getMessage().contains(expectedMessage));
    }

    @Test
    public void testResourceAllocation() throws InterruptedException {
        // Register a worker with limited resources.
        WorkerNode worker1 = new WorkerNode("worker-1", new Resource(2, 2048));
        scheduler.registerWorker(worker1);

        // Create a task that requires more resources than available on worker1.
        Task heavyTask = new Task("heavy", new Resource(4, 4096), "echo heavy", Collections.emptyList(), 5);
        scheduler.submitTask(heavyTask);

        // The heavy task should not be scheduled until another worker with sufficient resources is added.
        scheduler.executeAll();
        assertEquals(TaskStatus.PENDING, scheduler.getTaskStatus("heavy"));

        // Register another worker with sufficient resources.
        WorkerNode worker2 = new WorkerNode("worker-2", new Resource(4, 4096));
        scheduler.registerWorker(worker2);

        scheduler.executeAll();
        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("heavy"));
    }

    @Test
    public void testWorkerFailureReschedulesTask() throws InterruptedException {
        // Register two worker nodes.
        WorkerNode worker1 = new WorkerNode("worker-1", new Resource(4, 4096));
        WorkerNode worker2 = new WorkerNode("worker-2", new Resource(4, 4096));
        scheduler.registerWorker(worker1);
        scheduler.registerWorker(worker2);

        // Create a task with no dependencies.
        Task task = new Task("task-failure", new Resource(2, 2048), "echo FaultTolerance", Collections.emptyList(), 5);
        scheduler.submitTask(task);

        // Start execution in a separate thread.
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(() -> scheduler.executeAll());

        // Simulate a failure on the worker executing the task.
        // Wait a bit to let the task start.
        Thread.sleep(100);
        String assignedWorker = scheduler.getTaskAssignedWorker("task-failure");
        scheduler.simulateWorkerFailure(assignedWorker);

        // Wait to let the scheduler reschedule and complete the task.
        executor.shutdown();
        executor.awaitTermination(3, TimeUnit.SECONDS);

        assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("task-failure"));
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testConcurrentSubmissions() throws InterruptedException {
        WorkerNode worker = new WorkerNode("worker-1", new Resource(16, 16384));
        scheduler.registerWorker(worker);

        int numberOfTasks = 50;
        ExecutorService executor = Executors.newFixedThreadPool(5);
        CountDownLatch latch = new CountDownLatch(numberOfTasks);

        // Concurrently submit tasks.
        for (int i = 0; i < numberOfTasks; i++) {
            final int taskNumber = i;
            executor.submit(() -> {
                Task t = new Task("concurrent-" + taskNumber, new Resource(1, 512), "echo Task" + taskNumber, Collections.emptyList(), taskNumber % 10);
                scheduler.submitTask(t);
                latch.countDown();
            });
        }
        latch.await();
        executor.shutdown();

        scheduler.executeAll();

        // Verify that all tasks are completed.
        for (int i = 0; i < numberOfTasks; i++) {
            assertEquals(TaskStatus.COMPLETED, scheduler.getTaskStatus("concurrent-" + i));
        }
    }
}