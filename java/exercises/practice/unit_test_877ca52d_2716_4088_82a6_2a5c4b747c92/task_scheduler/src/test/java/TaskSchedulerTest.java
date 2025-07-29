import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

// Assuming that the solution code provides the following classes and method signatures:
// - A class "Task" with a constructor: Task(int taskId, int duration, int deadline, List<Integer> dependencies)
// - A class "TaskScheduler" with a static method: List<Integer> scheduleTasks(int N, List<Task> tasks)
//
// The tests below construct inputs using the Task class and then invoke TaskScheduler.scheduleTasks.

public class TaskSchedulerTest {

    // Helper method: verifies that the schedule is a valid permutation and respects dependency order
    private boolean isValidSchedule(List<Integer> schedule, Map<Integer, Task> taskMap) {
        // Check that schedule contains each task exactly once
        if (schedule.size() != taskMap.size()) {
            return false;
        }
        Set<Integer> seen = new HashSet<>();
        for (Integer taskId : schedule) {
            if (!taskMap.containsKey(taskId) || seen.contains(taskId)) {
                return false;
            }
            // For each dependency of the current task, ensure it is already scheduled
            for (Integer dep : taskMap.get(taskId).dependencies) {
                if (!seen.contains(dep)) {
                    return false;
                }
            }
            seen.add(taskId);
        }
        return true;
    }

    // Helper method: compute scheduling metrics: [missedDeadlinesCount, totalLateness]
    // Assumes tasks are executed sequentially in the order provided by "schedule".
    private int[] computeMetrics(List<Integer> schedule, Map<Integer, Task> taskMap) {
        int time = 0;
        int missedDeadlines = 0;
        int totalLateness = 0;
        for (Integer taskId : schedule) {
            Task task = taskMap.get(taskId);
            time += task.duration;
            int lateness = Math.max(0, time - task.deadline);
            totalLateness += lateness;
            if (time > task.deadline) {
                missedDeadlines++;
            }
        }
        return new int[] { missedDeadlines, totalLateness };
    }

    @Test
    public void testSimpleNoDependencies() {
        // Create tasks with no dependencies
        // Task format: (taskId, duration, deadline, dependencies)
        Task t1 = new Task(1, 3, 5, new ArrayList<>());
        Task t2 = new Task(2, 2, 6, new ArrayList<>());
        Task t3 = new Task(3, 1, 3, new ArrayList<>());

        List<Task> tasks = Arrays.asList(t1, t2, t3);
        int N = tasks.size();

        // Map for validation and metrics computation
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.taskId, t);
        }

        List<Integer> schedule = TaskScheduler.scheduleTasks(N, tasks);

        // Validate that schedule is a permutation of tasks and respects dependency order (trivial in this test)
        assertNotNull(schedule, "Schedule should not be null.");
        assertEquals(N, schedule.size(), "Schedule should contain all tasks.");
        assertTrue(isValidSchedule(schedule, taskMap), "Schedule must be a valid permutation with dependencies respected.");

        // Compute metrics: For this test, the optimal schedule should yield 0 missed deadlines and 0 total lateness.
        int[] metrics = computeMetrics(schedule, taskMap);
        assertEquals(0, metrics[0], "There should be no missed deadlines.");
        assertEquals(0, metrics[1], "Total lateness should be 0.");
    }

    @Test
    public void testDependencyOrdering() {
        // Tasks with dependencies:
        // Task 1: (duration 3, deadline 10, no dependencies)
        // Task 2: (duration 5, deadline 15, depends on 1)
        // Task 3: (duration 2, deadline 12, depends on 1)
        Task t1 = new Task(1, 3, 10, new ArrayList<>());
        Task t2 = new Task(2, 5, 15, new ArrayList<>(Arrays.asList(1)));
        Task t3 = new Task(3, 2, 12, new ArrayList<>(Arrays.asList(1)));

        List<Task> tasks = Arrays.asList(t1, t2, t3);
        int N = tasks.size();

        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.taskId, t);
        }

        List<Integer> schedule = TaskScheduler.scheduleTasks(N, tasks);

        // Validate schedule length and dependency ordering
        assertNotNull(schedule, "Schedule should not be null.");
        assertEquals(N, schedule.size(), "Schedule should contain exactly all tasks.");
        assertTrue(isValidSchedule(schedule, taskMap), "Schedule must respect dependency ordering.");

        // Optimal metrics: All tasks should be completed on time (0 missed deadlines, 0 lateness)
        int[] metrics = computeMetrics(schedule, taskMap);
        assertEquals(0, metrics[0], "No task should miss its deadline.");
        assertEquals(0, metrics[1], "Total lateness should be 0.");
    }

    @Test
    public void testCircularDependency() {
        // Create tasks with circular dependency:
        // Task 1 depends on 2 and Task 2 depends on 1.
        Task t1 = new Task(1, 3, 10, new ArrayList<>(Arrays.asList(2)));
        Task t2 = new Task(2, 5, 15, new ArrayList<>(Arrays.asList(1)));

        List<Task> tasks = Arrays.asList(t1, t2);
        int N = tasks.size();

        List<Integer> schedule = TaskScheduler.scheduleTasks(N, tasks);

        // In case of circular dependency, the function should return an empty list.
        assertNotNull(schedule, "Schedule should not be null even if circular dependencies exist.");
        assertEquals(0, schedule.size(), "Schedule should be empty when circular dependencies are present.");
    }

    @Test
    public void testComplexScenario() {
        // A more complex real-world scenario:
        // Task 1: (duration 4, deadline 8, no dependencies)
        // Task 2: (duration 2, deadline 10, depends on 1)
        // Task 3: (duration 3, deadline 7, depends on 1)
        // Task 4: (duration 1, deadline 12, depends on 2 and 3)
        // Task 5: (duration 6, deadline 20, depends on 1)
        Task t1 = new Task(1, 4, 8, new ArrayList<>());
        Task t2 = new Task(2, 2, 10, new ArrayList<>(Arrays.asList(1)));
        Task t3 = new Task(3, 3, 7, new ArrayList<>(Arrays.asList(1)));
        Task t4 = new Task(4, 1, 12, new ArrayList<>(Arrays.asList(2, 3)));
        Task t5 = new Task(5, 6, 20, new ArrayList<>(Arrays.asList(1)));

        List<Task> tasks = Arrays.asList(t1, t2, t3, t4, t5);
        int N = tasks.size();

        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.taskId, t);
        }

        List<Integer> schedule = TaskScheduler.scheduleTasks(N, tasks);

        // Validate schedule length and dependency ordering
        assertNotNull(schedule, "Schedule should not be null.");
        assertEquals(N, schedule.size(), "Schedule should contain all tasks.");
        assertTrue(isValidSchedule(schedule, taskMap), "Schedule must respect all dependency constraints.");

        // For this scenario, one optimal schedule is [1,3,2,4,5] which yields:
        // Time after tasks: 4,7,9,10,16 and all tasks meet their deadlines (0 lateness).
        int[] metrics = computeMetrics(schedule, taskMap);
        assertEquals(0, metrics[0], "No task should miss its deadline in the optimal schedule.");
        assertEquals(0, metrics[1], "Total lateness should be 0 in the optimal schedule.");
    }

    @Test
    public void testSingleTaskLate() {
        // Edge case: A single task that cannot be completed by its deadline.
        // Task 1: (duration 5, deadline 3, no dependencies)
        Task t1 = new Task(1, 5, 3, new ArrayList<>());
        List<Task> tasks = Arrays.asList(t1);
        int N = tasks.size();

        Map<Integer, Task> taskMap = new HashMap<>();
        taskMap.put(t1.taskId, t1);

        List<Integer> schedule = TaskScheduler.scheduleTasks(N, tasks);

        // Validate that the schedule contains the single task.
        assertNotNull(schedule, "Schedule should not be null.");
        assertEquals(1, schedule.size(), "Schedule should contain one task.");
        assertTrue(isValidSchedule(schedule, taskMap), "Schedule must be a valid ordering.");

        // The expected metrics: finish time 5, lateness = 2, one missed deadline.
        int[] metrics = computeMetrics(schedule, taskMap);
        assertEquals(1, metrics[0], "There should be one missed deadline.");
        assertEquals(2, metrics[1], "Total lateness should be 2.");
    }
}

// Dummy Task class for compilation of unit tests.
// In the actual project, this class is expected to be provided in the main source.
class Task {
    public int taskId;
    public int duration;
    public int deadline;
    public List<Integer> dependencies;

    public Task(int taskId, int duration, int deadline, List<Integer> dependencies) {
        this.taskId = taskId;
        this.duration = duration;
        this.deadline = deadline;
        // To avoid accidental external modifications, create a new list.
        this.dependencies = new ArrayList<>(dependencies);
    }
}