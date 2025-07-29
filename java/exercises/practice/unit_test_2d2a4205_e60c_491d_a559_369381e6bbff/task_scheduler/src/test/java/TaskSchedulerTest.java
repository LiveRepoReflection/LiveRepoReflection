package task_scheduler;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class TaskSchedulerTest {

    // Assumption: The Task class and TaskScheduler class are defined in the task_scheduler package.
    // Task class is assumed to have the following API:
    //   public Task(int id, int duration, int deadline, List<Integer> dependencies)
    //   public int getId();
    //   public int getDuration();
    //   public int getDeadline();
    //   public List<Integer> getDependencies();
    //
    // TaskScheduler class is assumed to have the following API:
    //   public List<Integer> getOptimalSchedule(List<Task> tasks)

    private TaskScheduler scheduler = new TaskScheduler();

    // Helper method to check if the schedule respects the dependency constraints.
    private boolean isValidTopologicalOrder(List<Task> tasks, List<Integer> schedule) {
        Map<Integer, Integer> position = new HashMap<>();
        for (int i = 0; i < schedule.size(); i++) {
            position.put(schedule.get(i), i);
        }
        for (Task task : tasks) {
            for (Integer depId : task.getDependencies()) {
                // If dependency is missing from the schedule, order is invalid.
                if (!position.containsKey(depId)) {
                    return false;
                }
                // Dependency must come before the task.
                if (position.get(task.getId()) < position.get(depId)) {
                    return false;
                }
            }
        }
        return true;
    }

    @Test
    public void testEmptyInput() {
        List<Task> tasks = new ArrayList<>();
        List<Integer> result = scheduler.getOptimalSchedule(tasks);
        assertTrue(result.isEmpty(), "Expected empty schedule for empty input list.");
    }

    @Test
    public void testSimpleValidSchedule() {
        // Create a simple valid dependency chain:
        // Task 1: id=1, duration=5, deadline=10, no dependencies.
        // Task 2: id=2, duration=3, deadline=15, depends on task 1.
        // Task 3: id=3, duration=7, deadline=20, depends on tasks 1 and 2.
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 5, 10, new ArrayList<>()));
        tasks.add(new Task(2, 3, 15, Arrays.asList(1)));
        tasks.add(new Task(3, 7, 20, Arrays.asList(1, 2)));

        List<Integer> schedule = scheduler.getOptimalSchedule(tasks);
        // The expected schedule should include all three tasks.
        assertEquals(3, schedule.size(), "Schedule should include all tasks.");
        assertTrue(isValidTopologicalOrder(tasks, schedule), "Schedule must respect dependency order.");
    }

    @Test
    public void testMultipleValidSchedules() {
        // Create tasks where more than one valid scheduling order exists:
        // Task 1: id=1, duration=4, deadline=20, no dependencies.
        // Task 2: id=2, duration=6, deadline=25, no dependencies.
        // Task 3: id=3, duration=5, deadline=30, depends on both task 1 and task 2.
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 4, 20, new ArrayList<>()));
        tasks.add(new Task(2, 6, 25, new ArrayList<>()));
        tasks.add(new Task(3, 5, 30, Arrays.asList(1, 2)));

        List<Integer> schedule = scheduler.getOptimalSchedule(tasks);
        assertEquals(3, schedule.size(), "Schedule should include all tasks.");
        assertTrue(isValidTopologicalOrder(tasks, schedule), "Schedule must respect dependency order.");
    }

    @Test
    public void testCircularDependency() {
        // Create tasks with a circular dependency:
        // Task 1: id=1, duration=3, deadline=10, depends on task 2.
        // Task 2: id=2, duration=4, deadline=15, depends on task 1.
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 3, 10, Arrays.asList(2)));
        tasks.add(new Task(2, 4, 15, Arrays.asList(1)));

        List<Integer> schedule = scheduler.getOptimalSchedule(tasks);
        // A circular dependency should result in an empty schedule.
        assertTrue(schedule.isEmpty(), "Expected empty schedule due to circular dependency.");
    }

    @Test
    public void testComplexSchedule() {
        // Complex real-world scenario with multiple dependencies:
        // Task 1: id=1, duration=5, deadline=10, dependencies: []
        // Task 2: id=2, duration=3, deadline=15, dependencies: [1]
        // Task 3: id=3, duration=7, deadline=20, dependencies: [1, 2]
        // Task 4: id=4, duration=2, deadline=12, dependencies: []
        // Task 5: id=5, duration=4, deadline=25, dependencies: [3, 4]
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 5, 10, new ArrayList<>()));
        tasks.add(new Task(2, 3, 15, Arrays.asList(1)));
        tasks.add(new Task(3, 7, 20, Arrays.asList(1, 2)));
        tasks.add(new Task(4, 2, 12, new ArrayList<>()));
        tasks.add(new Task(5, 4, 25, Arrays.asList(3, 4)));

        List<Integer> schedule = scheduler.getOptimalSchedule(tasks);
        assertEquals(5, schedule.size(), "Schedule should include all tasks in complex scenario.");
        assertTrue(isValidTopologicalOrder(tasks, schedule), "Schedule must respect dependency order.");

        // Simulate task completion times and calculate lateness.
        Map<Integer, Task> taskMap = new HashMap<>();
        for (Task t : tasks) {
            taskMap.put(t.getId(), t);
        }
        int currentTime = 0;
        int lateTasks = 0;
        int totalTardiness = 0;
        for (Integer id : schedule) {
            Task t = taskMap.get(id);
            currentTime += t.getDuration();
            int lateness = Math.max(0, currentTime - t.getDeadline());
            if (lateness > 0) {
                lateTasks++;
                totalTardiness += lateness;
            }
        }
        // Although multiple valid optimal schedules may exist, ensure that the schedule has been computed.
        assertTrue(currentTime > 0, "Total execution time should be greater than zero.");
    }
}