import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setUp() {
        // Assuming TaskScheduler has a no-argument constructor.
        scheduler = new TaskScheduler();
    }

    @Test
    public void testWorkerRegistrationAndHeartbeat() {
        Map<String, Integer> resources = new HashMap<>();
        resources.put("CPU", 8);
        resources.put("Memory", 16);
        resources.put("Disk", 100);
        Worker worker = new Worker("worker1", resources, 5);
        boolean registered = scheduler.registerWorker(worker);
        assertTrue(registered, "Worker should be registered successfully.");

        // Simulate heartbeats
        assertDoesNotThrow(() -> {
            for (int i = 0; i < 3; i++) {
                scheduler.workerHeartbeat("worker1");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
        });
    }

    @Test
    public void testTaskSubmissionAndScheduling() {
        // Register a worker with sufficient resources.
        Map<String, Integer> workerResources = new HashMap<>();
        workerResources.put("CPU", 4);
        workerResources.put("Memory", 8);
        workerResources.put("Disk", 50);
        Worker worker = new Worker("workerA", workerResources, 5);
        scheduler.registerWorker(worker);

        // Submit a high priority task that fits on the worker.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 2);
        taskResources.put("Memory", 4);
        taskResources.put("Disk", 20);
        Task task = new Task("task1", 10, taskResources, 30, "client1");
        boolean submitted = scheduler.submitTask(task);
        assertTrue(submitted, "Task should be submitted successfully.");

        // Trigger scheduling process.
        scheduler.processScheduling();

        List<Task> assignedTasks = scheduler.getTasksForWorker("workerA");
        assertNotNull(assignedTasks, "Worker task list should not be null.");
        assertTrue(assignedTasks.stream().anyMatch(t -> t.getTaskId().equals("task1")),
                   "Task with ID task1 should be scheduled to workerA.");
    }

    @Test
    public void testInsufficientResourcesQueueing() {
        // Register a worker with limited resources.
        Map<String, Integer> workerResources = new HashMap<>();
        workerResources.put("CPU", 2);
        workerResources.put("Memory", 4);
        Worker worker = new Worker("workerLimited", workerResources, 5);
        scheduler.registerWorker(worker);

        // Submit a task that requires more resources than available.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 4);
        taskResources.put("Memory", 8);
        Task heavyTask = new Task("heavyTask", 8, taskResources, 60, "client2");
        boolean submitted = scheduler.submitTask(heavyTask);
        assertTrue(submitted, "Heavy task should be accepted and queued if resources are insufficient.");

        // Process scheduling. Task should remain queued.
        scheduler.processScheduling();

        Task fetchedTask = scheduler.getTaskById("heavyTask");
        assertNotNull(fetchedTask, "Heavy task should be present in the system.");
        assertEquals(TaskState.QUEUED, fetchedTask.getState(), "Heavy task should be in QUEUED state due to insufficient resources.");
    }

    @Test
    public void testDuplicateTaskSubmission() {
        // Submit a task.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 1);
        taskResources.put("Memory", 2);
        Task task1 = new Task("dupTask", 5, taskResources, 20, "client3");
        boolean firstSubmission = scheduler.submitTask(task1);
        assertTrue(firstSubmission, "First submission of dupTask should succeed.");

        // Submit another task with the same ID. The design decision is to reject duplicates.
        Task duplicateTask = new Task("dupTask", 7, taskResources, 25, "client3");
        boolean secondSubmission = scheduler.submitTask(duplicateTask);
        assertFalse(secondSubmission, "Duplicate task submission should be rejected.");
    }

    @Test
    public void testPriorityScheduling() {
        // Register a worker with ample resources.
        Map<String, Integer> workerResources = new HashMap<>();
        workerResources.put("CPU", 8);
        workerResources.put("Memory", 16);
        Worker worker = new Worker("workerPriority", workerResources, 5);
        scheduler.registerWorker(worker);

        // Submit two tasks with different priorities.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 2);
        taskResources.put("Memory", 4);
        Task lowPriorityTask = new Task("taskLow", 3, taskResources, 30, "client4");
        Task highPriorityTask = new Task("taskHigh", 10, taskResources, 30, "client4");

        scheduler.submitTask(lowPriorityTask);
        scheduler.submitTask(highPriorityTask);

        scheduler.processScheduling();
        List<Task> tasksOnWorker = scheduler.getTasksForWorker("workerPriority");
        assertNotNull(tasksOnWorker, "The worker should have assigned tasks.");
        // Expect high priority task to be scheduled before low priority task.
        int indexHigh = -1, indexLow = -1;
        for (int i = 0; i < tasksOnWorker.size(); i++) {
            if (tasksOnWorker.get(i).getTaskId().equals("taskHigh")) {
                indexHigh = i;
            }
            if (tasksOnWorker.get(i).getTaskId().equals("taskLow")) {
                indexLow = i;
            }
        }
        assertTrue(indexHigh != -1 && indexLow != -1, "Both tasks should be scheduled.");
        assertTrue(indexHigh < indexLow, "High priority task should be assigned before low priority task.");
    }

    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testWorkerFailureAndTaskRescheduling() {
        // Register two workers.
        Map<String, Integer> workerResources1 = new HashMap<>();
        workerResources1.put("CPU", 4);
        workerResources1.put("Memory", 8);
        Worker worker1 = new Worker("worker1", workerResources1, 5);
        scheduler.registerWorker(worker1);

        Map<String, Integer> workerResources2 = new HashMap<>();
        workerResources2.put("CPU", 4);
        workerResources2.put("Memory", 8);
        Worker worker2 = new Worker("worker2", workerResources2, 5);
        scheduler.registerWorker(worker2);

        // Submit a task that can be executed by either worker.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 2);
        taskResources.put("Memory", 4);
        Task task = new Task("reschedTask", 6, taskResources, 40, "client5");
        scheduler.submitTask(task);
        scheduler.processScheduling();

        // Determine which worker got the task.
        String assignedWorkerId = null;
        if (scheduler.getTasksForWorker("worker1").stream().anyMatch(t -> t.getTaskId().equals("reschedTask"))) {
            assignedWorkerId = "worker1";
        } else if (scheduler.getTasksForWorker("worker2").stream().anyMatch(t -> t.getTaskId().equals("reschedTask"))) {
            assignedWorkerId = "worker2";
        }
        assertNotNull(assignedWorkerId, "Task should be scheduled to one of the workers.");

        // Simulate worker failure.
        scheduler.simulateWorkerFailure(assignedWorkerId);

        // Process scheduling again so that the task can be rescheduled.
        scheduler.processScheduling();

        // Verify that the task is now assigned to the other worker.
        String newAssignedWorkerId = null;
        if (assignedWorkerId.equals("worker1") && scheduler.getTasksForWorker("worker2").stream().anyMatch(t -> t.getTaskId().equals("reschedTask"))) {
            newAssignedWorkerId = "worker2";
        } else if (assignedWorkerId.equals("worker2") && scheduler.getTasksForWorker("worker1").stream().anyMatch(t -> t.getTaskId().equals("reschedTask"))) {
            newAssignedWorkerId = "worker1";
        }
        assertNotNull(newAssignedWorkerId, "Task should be rescheduled to the available worker after failure.");
    }

    @Test
    public void testClientFairness() {
        // Register a worker with high capacity.
        Map<String, Integer> resources = new HashMap<>();
        resources.put("CPU", 16);
        resources.put("Memory", 32);
        Worker worker = new Worker("workerFair", resources, 5);
        scheduler.registerWorker(worker);

        // Submit tasks from two different clients.
        Map<String, Integer> taskResources = new HashMap<>();
        taskResources.put("CPU", 2);
        taskResources.put("Memory", 4);
        for (int i = 1; i <= 5; i++) {
            Task taskClientA = new Task("A_task" + i, 5, taskResources, 20, "clientA");
            Task taskClientB = new Task("B_task" + i, 5, taskResources, 20, "clientB");
            scheduler.submitTask(taskClientA);
            scheduler.submitTask(taskClientB);
        }

        scheduler.processScheduling();
        List<Task> tasksOnWorker = scheduler.getTasksForWorker("workerFair");
        assertNotNull(tasksOnWorker, "Worker should have a list of tasks scheduled.");

        // Verify fairness constraint: each client should have at most a limited number of concurrent tasks.
        int clientACount = 0;
        int clientBCount = 0;
        for (Task t : tasksOnWorker) {
            if (t.getClientId().equals("clientA")) {
                clientACount++;
            } else if (t.getClientId().equals("clientB")) {
                clientBCount++;
            }
        }
        // Assume a fairness limit of 3 concurrent tasks per client.
        assertTrue(clientACount <= 3, "Client A should not exceed the fairness limit of concurrent tasks.");
        assertTrue(clientBCount <= 3, "Client B should not exceed the fairness limit of concurrent tasks.");
    }
}