package task_scheduler;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;

public class TaskSchedulerTest {

    // Helper method to create a Task object.
    // Assumes a Task class with the following constructor:
    // Task(int id, int duration, int deadline, List<Integer> dependencies)
    private Task createTask(int id, int duration, int deadline, Integer... deps) {
        List<Integer> dependencies = new ArrayList<>(Arrays.asList(deps));
        return new Task(id, duration, deadline, dependencies);
    }
    
    @Test
    public void testSingleTaskFeasible() {
        // Single task with no dependencies and feasible deadline.
        Task task = createTask(1, 2, 5);
        List<Task> tasks = List.of(task);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // Since the task can complete before its deadline, total lateness is 0.
        Assertions.assertEquals(0, result);
    }
    
    @Test
    public void testChainTasksFeasible() {
        // Chain of tasks with dependencies that can all meet deadlines.
        // Task 1 -> Task 2 -> Task 3.
        Task task1 = createTask(1, 2, 3);
        Task task2 = createTask(2, 3, 6, 1);
        Task task3 = createTask(3, 1, 8, 2);
        List<Task> tasks = List.of(task1, task2, task3);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // Feasible schedule: finish times 2, 5, and 6 respectively. All deadlines met.
        Assertions.assertEquals(0, result);
    }
    
    @Test
    public void testSingleTaskImpossible() {
        // Single task that cannot complete before its deadline.
        Task task = createTask(1, 2, 1);
        List<Task> tasks = List.of(task);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // Since the task cannot complete before deadline, return -1.
        Assertions.assertEquals(-1, result);
    }
    
    @Test
    public void testIndependentTasksImpossible() {
        // Two independent tasks that cannot both be scheduled to meet their deadlines.
        // Task 1 and Task 2 have no dependencies.
        Task task1 = createTask(1, 3, 4);
        Task task2 = createTask(2, 2, 3);
        List<Task> tasks = List.of(task1, task2);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // No ordering can satisfy both deadlines.
        Assertions.assertEquals(-1, result);
    }
    
    @Test
    public void testMultipleDependenciesFeasible() {
        // More complex structure with multiple dependencies.
        // Structure:
        //         Task 1
        //         /    \
        //     Task 2   Task 3
        //         \    /
        //         Task 4
        Task task1 = createTask(1, 2, 5);
        Task task2 = createTask(2, 4, 10, 1);
        Task task3 = createTask(3, 3, 9, 1);
        Task task4 = createTask(4, 2, 11, 2, 3);
        List<Task> tasks = List.of(task1, task2, task3, task4);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // One feasible scheduling order:
        // Task1 finishes at 2, Task2 at 6, Task3 at 9, Task4 at 11.
        // All deadlines are met.
        Assertions.assertEquals(0, result);
    }
    
    @Test
    public void testMultipleComponentsFeasible() {
        // Two disjoint sets of tasks that can be scheduled independently.
        // Component 1: Task 1 -> Task 2.
        // Component 2: Task 3 (independent).
        Task task1 = createTask(1, 2, 4);
        Task task2 = createTask(2, 3, 8, 1);
        Task task3 = createTask(3, 1, 2);
        List<Task> tasks = List.of(task1, task2, task3);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // Feasible scheduling:
        // For example, run task3 first (finishing at 1 <= 2),
        // then task1 (finishing at 1+2=3 <=4) and task2 (finishing at 3+3=6 <=8).
        Assertions.assertEquals(0, result);
    }
    
    @Test
    public void testComplexOrderingImpossible() {
        // Complex dependency graph where deadline conflicts make it impossible.
        // Structure: Task 1 -> Task 2, Task 3 independent.
        // Deadlines are set such that regardless of order, one task will be late.
        Task task1 = createTask(1, 3, 3);
        Task task2 = createTask(2, 2, 4, 1);
        Task task3 = createTask(3, 2, 3);
        List<Task> tasks = List.of(task1, task2, task3);
        int result = Scheduler.calculateMinimumTotalLateness(tasks);
        // It is impossible to schedule both components to complete before deadlines.
        Assertions.assertEquals(-1, result);
    }
}