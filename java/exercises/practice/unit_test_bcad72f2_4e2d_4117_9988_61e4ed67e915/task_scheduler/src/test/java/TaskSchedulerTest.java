import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setup() {
        scheduler = new TaskScheduler();
    }

    @Test
    public void testNoTasks() {
        List<WorkerNode> workerNodes = new ArrayList<>();
        workerNodes.add(new WorkerNode("worker1", 4, 8, 10));
        workerNodes.add(new WorkerNode("worker2", 2, 4, 5));

        List<Task> tasks = new ArrayList<>();

        Schedule schedule = scheduler.scheduleTasks(workerNodes, tasks);
        assertNotNull(schedule, "Schedule should not be null for empty task list");
        assertTrue(schedule.getTaskAssignments().isEmpty(), "No tasks should be assigned");
        assertEquals(0, schedule.getMakespan(), "Makespan should be 0 when no tasks are scheduled");
    }

    @Test
    public void testSingleTask() {
        WorkerNode worker = new WorkerNode("worker1", 4, 8, 10);
        List<WorkerNode> workerNodes = Collections.singletonList(worker);

        Task task = new Task("task1", 2, 4, 5, new HashSet<>(), 10);
        List<Task> tasks = Collections.singletonList(task);

        Schedule schedule = scheduler.scheduleTasks(workerNodes, tasks);
        assertNotNull(schedule, "Schedule should not be null");
        Map<String, String> assignments = schedule.getTaskAssignments();
        assertEquals(1, assignments.size(), "There should be exactly one assignment");
        assertEquals("worker1", assignments.get("task1"), "Task should be assigned to worker1");
        assertEquals(10, schedule.getMakespan(), "Makespan should equal the task runtime");
    }

    @Test
    public void testMultipleTasksWithDependencies() {
        WorkerNode worker1 = new WorkerNode("worker1", 4, 8, 10);
        WorkerNode worker2 = new WorkerNode("worker2", 3, 6, 8);
        List<WorkerNode> workerNodes = Arrays.asList(worker1, worker2);

        // Task A has no dependency; Task B depends on A; Task C has no dependency; Task D depends on both A and C.
        Task taskA = new Task("A", 2, 4, 5, new HashSet<>(), 10);
        Task taskB = new Task("B", 1, 2, 2, new HashSet<>(Arrays.asList("A")), 5);
        Task taskC = new Task("C", 1, 2, 3, new HashSet<>(), 8);
        Task taskD = new Task("D", 2, 3, 4, new HashSet<>(Arrays.asList("A", "C")), 7);

        List<Task> tasks = Arrays.asList(taskA, taskB, taskC, taskD);

        Schedule schedule = scheduler.scheduleTasks(workerNodes, tasks);
        assertNotNull(schedule, "Schedule should not be null");
        Map<String, String> assignments = schedule.getTaskAssignments();
        assertEquals(4, assignments.size(), "All tasks must be assigned a worker");

        // Validate that each task is assigned to a worker that has sufficient capacity.
        Map<String, WorkerNode> workerLookup = new HashMap<>();
        for (WorkerNode w : workerNodes) {
            workerLookup.put(w.getId(), w);
        }
        for (Task t : tasks) {
            String workerId = assignments.get(t.getId());
            assertNotNull(workerId, "Every task should be assigned a worker");
            WorkerNode worker = workerLookup.get(workerId);
            assertNotNull(worker, "Assigned worker must exist");
            assertTrue(t.getCpuRequirement() <= worker.getCpuCapacity(),
                "Worker " + worker.getId() + " must have sufficient CPU for task " + t.getId());
            assertTrue(t.getMemoryRequirement() <= worker.getMemoryCapacity(),
                "Worker " + worker.getId() + " must have sufficient memory for task " + t.getId());
            assertTrue(t.getDiskRequirement() <= worker.getDiskCapacity(),
                "Worker " + worker.getId() + " must have sufficient disk for task " + t.getId());
        }

        // Basic check on makespan: it must be at least as long as the longest single task.
        int maxRuntime = tasks.stream().mapToInt(Task::getEstimatedRunTime).max().orElse(0);
        assertTrue(schedule.getMakespan() >= maxRuntime,
            "Makespan should be at least as long as the longest single task runtime");
    }

    @Test
    public void testCyclicDependencies() {
        WorkerNode worker = new WorkerNode("worker1", 4, 8, 10);
        List<WorkerNode> workerNodes = Collections.singletonList(worker);

        // Create cyclic dependency: task1 depends on task2, and task2 depends on task1.
        Task task1 = new Task("task1", 2, 4, 5, new HashSet<>(Arrays.asList("task2")), 10);
        Task task2 = new Task("task2", 1, 2, 2, new HashSet<>(Arrays.asList("task1")), 5);
        List<Task> tasks = Arrays.asList(task1, task2);

        Schedule schedule = scheduler.scheduleTasks(workerNodes, tasks);
        // For cyclic dependencies, no valid schedule is possible; so makespan should be -1.
        assertNotNull(schedule, "Schedule object should be returned even if scheduling fails");
        assertEquals(-1, schedule.getMakespan(), "Makespan should be -1 when cyclic dependencies occur");
    }

    @Test
    public void testInsufficientResources() {
        // Worker has limited resources.
        WorkerNode worker = new WorkerNode("worker1", 2, 2, 2);
        List<WorkerNode> workerNodes = Collections.singletonList(worker);

        // Task requires more resources than available.
        Task task = new Task("task1", 3, 3, 3, new HashSet<>(), 10);
        List<Task> tasks = Collections.singletonList(task);

        Schedule schedule = scheduler.scheduleTasks(workerNodes, tasks);
        assertNotNull(schedule, "Schedule object should be returned even if scheduling fails");
        // For insufficient resources, no valid schedule is possible; therefore makespan should be -1.
        assertEquals(-1, schedule.getMakespan(), "Makespan should be -1 when task requirements exceed worker's capacity");
    }
}