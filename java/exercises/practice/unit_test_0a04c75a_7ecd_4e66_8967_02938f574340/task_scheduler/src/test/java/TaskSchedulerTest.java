import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setUp() {
        scheduler = new TaskScheduler();
    }

    @Test
    public void testAssignTaskWithoutDependencies() {
        // Add a worker with required resource "CPU"
        int workerId = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU")));
        // Add a task that requires "CPU", with no dependencies, estimated time 100 ms, priority 1
        int taskId = scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 100, 1);

        // Initially, the task status should be "Ready"
        assertEquals("Ready", scheduler.getTaskStatus(taskId));

        // Assign tasks to available workers
        scheduler.assignTasks();

        // Verify that the worker has been assigned the task and its status is "Running"
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertTrue(assignments.containsKey(workerId));
        assertEquals(taskId, assignments.get(workerId));
        assertEquals("Running", scheduler.getTaskStatus(taskId));
    }

    @Test
    public void testAssignTaskWithDependencies() {
        // Add two workers with sufficient resources
        int worker1 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory")));
        int worker2 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory")));

        // Task 1: No dependencies, requires "CPU"
        int task1 = scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 100, 1);
        // Task 2: Depends on task1, requires "Memory"
        int task2 = scheduler.addTask(new HashSet<>(Arrays.asList("Memory")), Arrays.asList(task1), 150, 2);

        scheduler.assignTasks();

        // Only task1 should be assigned since task2 is blocked by dependency
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertTrue(assignments.containsValue(task1));
        assertFalse(assignments.containsValue(task2));
        assertEquals("Running", scheduler.getTaskStatus(task1));
        assertEquals("Blocked", scheduler.getTaskStatus(task2));

        // Mark task1 as completed to unblock task2
        scheduler.markTaskCompleted(task1);

        // Reassign tasks after task1 completion
        scheduler.assignTasks();
        assignments = scheduler.getWorkerTaskAssignments();
        // Task2 should now get assigned
        assertTrue(assignments.containsValue(task2));
        assertEquals("Completed", scheduler.getTaskStatus(task1));
        assertEquals("Running", scheduler.getTaskStatus(task2));
    }

    @Test
    public void testResourceConstraint() {
        // Add a worker that only has "CPU"
        int workerId = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU")));
        // Add a task that requires "Memory"
        int taskId = scheduler.addTask(new HashSet<>(Arrays.asList("Memory")), Collections.emptyList(), 120, 1);

        scheduler.assignTasks();

        // The task should remain "Ready" as no worker satisfies the required resource
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertFalse(assignments.containsValue(taskId));
        assertEquals("Ready", scheduler.getTaskStatus(taskId));
    }

    @Test
    public void testPriorityAssignment() {
        // Add a single worker with resources "CPU" and "Memory"
        int workerId = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory")));

        // Add two tasks with the same resource requirements but different priorities
        int lowPriorityTask = scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 150, 1);
        int highPriorityTask = scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 150, 3);

        scheduler.assignTasks();

        // The higher priority task should be assigned to the worker
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertEquals(highPriorityTask, assignments.get(workerId));
        assertEquals("Running", scheduler.getTaskStatus(highPriorityTask));
        assertEquals("Ready", scheduler.getTaskStatus(lowPriorityTask));
    }

    @Test
    public void testLeastResourceWorkerAssignment() {
        // Two workers: Worker1 has more resources than Worker2
        int worker1 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory", "Disk")));
        int worker2 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory")));

        // Add a task that requires "CPU" and "Memory"
        int taskId = scheduler.addTask(new HashSet<>(Arrays.asList("CPU", "Memory")), Collections.emptyList(), 100, 1);

        scheduler.assignTasks();

        // The task should be assigned to worker2 as it has fewer resources
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertTrue(assignments.containsKey(worker2));
        assertEquals(taskId, assignments.get(worker2));
        // Worker1 should remain idle because it has more resources than needed.
        assertFalse(assignments.containsKey(worker1));
    }

    @Test
    public void testRemoveTaskAndWorker() {
        // Add a worker and a task, then assign the task
        int workerId = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU")));
        int taskId = scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 100, 1);
        scheduler.assignTasks();

        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        assertTrue(assignments.containsKey(workerId));

        // Remove the task from the scheduler
        scheduler.removeTask(taskId);
        // Expect an exception when querying the status of a removed task
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            scheduler.getTaskStatus(taskId);
        });

        // Remove the worker and verify that it is no longer in assignments
        scheduler.removeWorker(workerId);
        assignments = scheduler.getWorkerTaskAssignments();
        assertFalse(assignments.containsKey(workerId));
    }

    @Test
    public void testConcurrentAssignments() throws InterruptedException {
        // Add two workers with sufficient resources
        int worker1 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory", "Disk")));
        int worker2 = scheduler.addWorker(new HashSet<>(Arrays.asList("CPU", "Memory")));

        // Runnable to add tasks concurrently
        Runnable taskProducer = () -> {
            for (int i = 0; i < 50; i++) {
                scheduler.addTask(new HashSet<>(Arrays.asList("CPU")), Collections.emptyList(), 100, 1);
            }
        };

        // Runnable to assign tasks repeatedly
        Runnable assigner = () -> {
            for (int i = 0; i < 20; i++) {
                scheduler.assignTasks();
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        };

        Thread producerThread1 = new Thread(taskProducer);
        Thread producerThread2 = new Thread(taskProducer);
        Thread assignerThread = new Thread(assigner);

        producerThread1.start();
        producerThread2.start();
        assignerThread.start();

        producerThread1.join();
        producerThread2.join();
        assignerThread.join();

        // Verify that all tasks assigned in concurrent environment have status "Running"
        Map<Integer, Integer> assignments = scheduler.getWorkerTaskAssignments();
        for (Integer assignedTaskId : assignments.values()) {
            assertEquals("Running", scheduler.getTaskStatus(assignedTaskId));
        }
    }
}