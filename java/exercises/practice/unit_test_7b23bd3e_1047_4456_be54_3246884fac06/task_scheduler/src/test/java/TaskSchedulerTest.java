import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import org.junit.jupiter.api.Test;

public class TaskSchedulerTest {

    // Helper task class used for testing
    // It is assumed that the main solution uses a similar Task definition.
    static class Task {
        int id;
        int duration;
        int deadline;
        List<Integer> dependencies;

        Task(int id, int duration, int deadline, List<Integer> dependencies) {
            this.id = id;
            this.duration = duration;
            this.deadline = deadline;
            this.dependencies = dependencies;
        }
    }

    // It is assumed that the main solution has a method with the following signature:
    // public static int minPenalty(List<Task> tasks)
    // which returns the minimum total penalty or Integer.MAX_VALUE if no valid schedule exists.

    // Test 1: Empty Task List
    @Test
    public void testEmptyTaskList() {
        List<Task> tasks = new ArrayList<>();
        int penalty = TaskScheduler.minPenalty(tasks);
        assertEquals(0, penalty, "Empty task list should incur 0 penalty.");
    }

    // Test 2: Single Task that finishes before deadline
    @Test
    public void testSingleTaskOnTime() {
        Task task = new Task(1, 10, 20, new ArrayList<>());
        List<Task> tasks = Collections.singletonList(task);
        int penalty = TaskScheduler.minPenalty(tasks);
        assertEquals(0, penalty, "Single task finishing on time should incur 0 penalty.");
    }

    // Test 3: Single Task that finishes after deadline
    @Test
    public void testSingleTaskLate() {
        Task task = new Task(1, 15, 10, new ArrayList<>());
        List<Task> tasks = Collections.singletonList(task);
        int penalty = TaskScheduler.minPenalty(tasks);
        // Completion time: 15, deadline: 10, penalty: 5
        assertEquals(5, penalty, "Single task finishing late should incur penalty equal to lateness.");
    }

    // Test 4: Multiple Tasks with dependencies and on time
    @Test
    public void testMultipleTasksNoPenalty() {
        Task task1 = new Task(1, 10, 20, new ArrayList<>());
        Task task2 = new Task(2, 15, 30, Arrays.asList(1));
        Task task3 = new Task(3, 5, 40, Arrays.asList(2));
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        int penalty = TaskScheduler.minPenalty(tasks);
        // Expected schedule: 1 (finishes at 10), 2 (finishes at 25), 3 (finishes at 30)
        // Penalties: 0, 0, 0 -> Total = 0
        assertEquals(0, penalty, "Valid dependency chain with tasks finishing on time should incur 0 penalty.");
    }

    // Test 5: Multiple Tasks with dependencies and penalties
    @Test
    public void testMultipleTasksWithPenalty() {
        // Task 1: finishes at 20, deadline = 15 => penalty 5
        // Task 2: depends on task 1, duration 10, scheduled after task 1, finishes at 30, deadline = 25 => penalty 5
        // Task 3: depends on task 1, duration 20, scheduled after tasks 1 and 2 in optimal ordering, finishes at 50, deadline = 60 => penalty 0
        Task task1 = new Task(1, 20, 15, new ArrayList<>());
        Task task2 = new Task(2, 10, 25, Arrays.asList(1));
        Task task3 = new Task(3, 20, 60, Arrays.asList(1));
        List<Task> tasks = Arrays.asList(task1, task2, task3);
        int penalty = TaskScheduler.minPenalty(tasks);
        // Optimal schedule minimizes penalty: expected total penalty = 5 + 5 = 10
        assertEquals(10, penalty, "Multiple tasks with penalties should compute the optimal total penalty.");
    }

    // Test 6: Task with zero duration
    @Test
    public void testZeroDurationTask() {
        Task task1 = new Task(1, 0, 0, new ArrayList<>());
        Task task2 = new Task(2, 10, 10, Arrays.asList(1));
        List<Task> tasks = Arrays.asList(task1, task2);
        int penalty = TaskScheduler.minPenalty(tasks);
        // Task1 finishes at 0 (deadline 0) penalty = 0; Task2 finishes at 10 (deadline 10) penalty = 0
        assertEquals(0, penalty, "Tasks with zero duration should be handled correctly, resulting in 0 penalty if on time.");
    }

    // Test 7: Complex dependency structure with minimal penalty
    @Test
    public void testComplexDependencies() {
        Task task1 = new Task(1, 5, 5, new ArrayList<>());
        Task task2 = new Task(2, 10, 15, Arrays.asList(1));
        Task task3 = new Task(3, 8, 20, Arrays.asList(1));
        Task task4 = new Task(4, 7, 30, Arrays.asList(2, 3));
        Task task5 = new Task(5, 12, 40, Arrays.asList(3));
        List<Task> tasks = Arrays.asList(task1, task2, task3, task4, task5);
        int penalty = TaskScheduler.minPenalty(tasks);
        // One optimal schedule:
        // Order: 1 (finishes at 5, penalty 0), 2 (finishes at 15, penalty 0), 3 (finishes at 23, penalty 3),
        // 4 (finishes at 30, penalty 0), 5 (finishes at 42, penalty 2) => Total penalty = 5
        assertEquals(5, penalty, "Complex dependency scheduling should compute the minimal total penalty correctly.");
    }

    // Test 8: Circular dependency should yield no valid schedule
    @Test
    public void testCircularDependency() {
        // Introducing a circular dependency: Task 1 depends on Task 2 and Task 2 depends on Task 1.
        Task task1 = new Task(1, 10, 20, Arrays.asList(2));
        Task task2 = new Task(2, 10, 20, Arrays.asList(1));
        List<Task> tasks = Arrays.asList(task1, task2);
        int penalty = TaskScheduler.minPenalty(tasks);
        // For circular dependency, no valid schedule exists so penalty should be Integer.MAX_VALUE.
        assertEquals(Integer.MAX_VALUE, penalty, "Circular dependencies should result in Integer.MAX_VALUE penalty.");
    }
}