import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import java.util.*;

public class TaskSchedulerTest {

    // Helper class to represent a Task.
    public static class Task {
        int id;
        int duration;
        List<Integer> dependencies;
        Map<String, Integer> resourceRequirements;

        public Task(int id, int duration, List<Integer> dependencies, Map<String, Integer> resourceRequirements) {
            this.id = id;
            this.duration = duration;
            this.dependencies = dependencies;
            this.resourceRequirements = resourceRequirements;
        }
    }

    // In our implementation, the TaskScheduler class provides a static method scheduleTasks
    // which accepts a list of Task objects and a Map of available resources.
    // It returns a Map where the key is the task id and the value is the start time of that task.
    // In case no feasible schedule exists, it returns an empty Map.
    //
    // public static Map<Integer, Integer> scheduleTasks(List<Task> tasks, Map<String, Integer> availableResources)

    @Test
    public void testSingleTask() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> requirements = new HashMap<>();
        requirements.put("CPU", 2);
        requirements.put("RAM", 4);
        tasks.add(new Task(1, 10, new ArrayList<>(), requirements));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 4);
        availableResources.put("RAM", 8);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        assertNotNull(schedule);
        assertEquals(1, schedule.size());
        // The single task should start at time 0.
        assertEquals(0, schedule.get(1).intValue());
    }

    @Test
    public void testIndependentTasksConcurrency() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> req1 = new HashMap<>();
        req1.put("CPU", 2);
        req1.put("RAM", 4);
        tasks.add(new Task(1, 10, new ArrayList<>(), req1));

        Map<String, Integer> req2 = new HashMap<>();
        req2.put("CPU", 2);
        req2.put("RAM", 4);
        tasks.add(new Task(2, 5, new ArrayList<>(), req2));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 4);
        availableResources.put("RAM", 8);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        assertNotNull(schedule);
        // Since resources are sufficient, both tasks can start at time 0 concurrently.
        assertEquals(0, schedule.get(1).intValue());
        assertEquals(0, schedule.get(2).intValue());
    }

    @Test
    public void testTasksWithDependencies() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> requirements = new HashMap<>();
        requirements.put("CPU", 2);
        requirements.put("RAM", 4);

        // Task 1 has no dependencies.
        tasks.add(new Task(1, 10, new ArrayList<>(), requirements));
        // Task 2 depends on task 1.
        tasks.add(new Task(2, 5, Arrays.asList(1), requirements));
        // Task 3 depends on task 2.
        tasks.add(new Task(3, 3, Arrays.asList(2), requirements));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 2);
        availableResources.put("RAM", 4);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        assertNotNull(schedule);
        // Each task should start only after all its dependencies have finished.
        assertEquals(0, schedule.get(1).intValue());
        assertEquals(10, schedule.get(2).intValue());
        assertEquals(15, schedule.get(3).intValue());
    }

    @Test
    public void testTieBreaking() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> requirements = new HashMap<>();
        requirements.put("CPU", 2);
        requirements.put("RAM", 4);

        // Two independent tasks.
        // Task 1 has a longer duration.
        tasks.add(new Task(1, 8, new ArrayList<>(), requirements));
        tasks.add(new Task(2, 5, new ArrayList<>(), requirements));

        // Limiting available resources such that tasks cannot run concurrently.
        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 2);
        availableResources.put("RAM", 4);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        assertNotNull(schedule);
        // Expect task 1 (longer duration) to run first.
        assertEquals(0, schedule.get(1).intValue());
        assertEquals(8, schedule.get(2).intValue());
    }

    @Test
    public void testCircularDependency() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> requirements = new HashMap<>();
        requirements.put("CPU", 2);
        requirements.put("RAM", 4);

        // Create a circular dependency: task 1 depends on 2 and task 2 depends on 1.
        tasks.add(new Task(1, 10, Arrays.asList(2), requirements));
        tasks.add(new Task(2, 5, Arrays.asList(1), requirements));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 4);
        availableResources.put("RAM", 8);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        // The scheduler should return an empty schedule due to the circular dependency.
        assertTrue(schedule.isEmpty());
    }

    @Test
    public void testTaskExceedingResources() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> requirements = new HashMap<>();
        // This task requires more CPU than available.
        requirements.put("CPU", 16);
        requirements.put("RAM", 4);
        tasks.add(new Task(1, 10, new ArrayList<>(), requirements));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 8);
        availableResources.put("RAM", 8);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        // The scheduler should return an empty schedule if the task's resource requirements cannot be met.
        assertTrue(schedule.isEmpty());
    }

    @Test
    public void testComplexScheduling() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> reqSmall = new HashMap<>();
        reqSmall.put("CPU", 2);
        reqSmall.put("RAM", 4);

        Map<String, Integer> reqLarge = new HashMap<>();
        reqLarge.put("CPU", 4);
        reqLarge.put("RAM", 8);

        // Task 1: no dependencies, long duration, uses large resources.
        tasks.add(new Task(1, 15, new ArrayList<>(), reqLarge));
        // Task 2: depends on Task 1.
        tasks.add(new Task(2, 5, Arrays.asList(1), reqSmall));
        // Task 3: no dependency, moderate duration, uses small resources.
        tasks.add(new Task(3, 10, new ArrayList<>(), reqSmall));
        // Task 4: depends on Task 1 and Task 3.
        tasks.add(new Task(4, 7, Arrays.asList(1, 3), reqSmall));
        // Task 5: depends on Task 2.
        tasks.add(new Task(5, 3, Arrays.asList(2), reqSmall));

        Map<String, Integer> availableResources = new HashMap<>();
        availableResources.put("CPU", 6);
        availableResources.put("RAM", 12);

        Map<Integer, Integer> schedule = TaskScheduler.scheduleTasks(tasks, availableResources);
        assertNotNull(schedule);
        // Validate dependency constraints.
        // Task 2 should start after Task 1 finishes.
        assertTrue(schedule.get(2) >= schedule.get(1) + 15);
        // Task 4 should start after both Task 1 and Task 3 finish.
        int finish1 = schedule.get(1) + 15;
        int finish3 = schedule.get(3) + 10;
        assertTrue(schedule.get(4) >= Math.max(finish1, finish3));
        // Task 5 should start after Task 2 finishes.
        assertTrue(schedule.get(5) >= schedule.get(2) + 5);

        // Compute makespan (end time of the last finishing task).
        int makespan = 0;
        for (Task t : tasks) {
            makespan = Math.max(makespan, schedule.get(t.id) + t.duration);
        }
        // The makespan should be a positive value.
        assertTrue(makespan > 0);
    }
}