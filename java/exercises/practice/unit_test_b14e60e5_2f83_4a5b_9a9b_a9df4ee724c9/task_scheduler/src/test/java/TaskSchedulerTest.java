package task_scheduler;

import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    // Assumes that the solution class TaskScheduler has a static method with signature:
    // public static List<Integer> getOptimalSchedule(int N, int[] id, int[] duration, int[] deadline,
    //     List<List<Integer>> dependencies, int[] priority)
    // which returns an ordered list of task ids representing the optimal schedule.

    @Test
    public void testSingleTaskCompletable() {
        int N = 1;
        int[] id = {0};
        int[] duration = {5};
        int[] deadline = {10};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        int[] priority = {100};

        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        List<Integer> expected = Arrays.asList(0);
        assertEquals(expected, result, "Single task should be scheduled when it can complete before its deadline.");
    }

    @Test
    public void testSingleTaskMissDeadline() {
        int N = 1;
        int[] id = {0};
        int[] duration = {10};
        int[] deadline = {5};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        int[] priority = {50};

        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        List<Integer> expected = new ArrayList<>();
        assertEquals(expected, result, "Task that misses its deadline should not be scheduled.");
    }

    @Test
    public void testMultipleTasksAllCompletable() {
        int N = 4;
        int[] id = {0, 1, 2, 3};
        int[] duration = {2, 3, 1, 2};
        int[] deadline = {10, 10, 10, 10};
        int[] priority = {10, 20, 30, 40};

        // Dependencies:
        // Task 1 depends on 0, Task 2 depends on 0, and Task 3 depends on 1 and 2.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());         // Task 0
        dependencies.add(Arrays.asList(0));            // Task 1
        dependencies.add(Arrays.asList(0));            // Task 2
        dependencies.add(Arrays.asList(1, 2));         // Task 3

        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        // Due to tie-breaking rules and dependencies, both [0,2,1,3] and [0,1,2,3] may be valid.
        List<Integer> validOption1 = Arrays.asList(0, 2, 1, 3);
        List<Integer> validOption2 = Arrays.asList(0, 1, 2, 3);
        boolean valid = result.equals(validOption1) || result.equals(validOption2);
        assertTrue(valid, "Multiple tasks with dependencies should be scheduled in a valid order.");
    }

    @Test
    public void testTasksWithPartialCompletion() {
        // Only some tasks can complete before their deadlines.
        int N = 3;
        int[] id = {0, 1, 2};
        int[] duration = {3, 5, 2};
        int[] deadline = {6, 7, 10};
        int[] priority = {50, 100, 70};

        // Dependencies:
        // Task 1 depends on 0, Task 2 depends on 0.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());             // Task 0
        dependencies.add(Arrays.asList(0));                // Task 1
        dependencies.add(Arrays.asList(0));                // Task 2

        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        // The optimal schedule should complete tasks that meet deadlines. For instance, scheduling task 0 then task 2:
        // Task 0 finishes at 3, Task 2 finishes at 5 (both within deadlines), while Task 1 would miss its deadline.
        List<Integer> expected = Arrays.asList(0, 2);
        assertEquals(expected, result, "Schedule should include only tasks that can complete before their deadlines.");
    }

    @Test
    public void testTieBreakingRules() {
        // Test tie-breaking when tasks have identical overall priority.
        int N = 4;
        int[] id = {0, 1, 2, 3};
        int[] duration = {2, 2, 2, 2};
        int[] deadline = {10, 8, 8, 10};
        int[] priority = {10, 10, 10, 10};

        // No dependencies among tasks.
        List<List<Integer>> dependencies = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            dependencies.add(new ArrayList<>());
        }

        // Expected ordering:
        // Tasks with deadline 8: tasks 1 and 2 should come first, with the higher id (2) preceding the lower (1).
        // Then tasks with deadline 10: tasks 0 and 3, where higher id (3) precedes lower id (0).
        List<Integer> expected = Arrays.asList(2, 1, 3, 0);
        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        assertEquals(expected, result, "Tie-breaking rules should produce the expected ordering.");
    }

    @Test
    public void testComplexDependencies() {
        int N = 6;
        int[] id = {0, 1, 2, 3, 4, 5};
        int[] duration = {3, 2, 4, 1, 2, 3};
        int[] deadline = {10, 9, 14, 6, 12, 15};
        int[] priority = {20, 15, 30, 10, 25, 5};

        // Dependencies:
        // Task 1 depends on Task 0.
        // Task 2 depends on Task 0.
        // Task 3 depends on Task 1 and Task 2.
        // Task 4 depends on Task 1.
        // Task 5 depends on Task 3 and Task 4.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());             // Task 0
        dependencies.add(Arrays.asList(0));                // Task 1
        dependencies.add(Arrays.asList(0));                // Task 2
        dependencies.add(Arrays.asList(1, 2));             // Task 3
        dependencies.add(Arrays.asList(1));                // Task 4
        dependencies.add(Arrays.asList(3, 4));             // Task 5

        List<Integer> result = TaskScheduler.getOptimalSchedule(N, id, duration, deadline, dependencies, priority);
        // Validate that the returned schedule respects dependencies.
        Map<Integer, Integer> position = new HashMap<>();
        for (int i = 0; i < result.size(); i++) {
            position.put(result.get(i), i);
        }
        for (int i = 0; i < N; i++) {
            for (int dep : dependencies.get(i)) {
                if (position.containsKey(i) && position.containsKey(dep)) {
                    assertTrue(position.get(dep) < position.get(i),
                            "Task " + i + " should appear after its dependency " + dep);
                }
            }
        }
        // Validate that every scheduled task meets its deadline.
        int currentTime = 0;
        for (int taskId : result) {
            currentTime += duration[taskId];
            assertTrue(currentTime <= deadline[taskId],
                    "Task " + taskId + " finishes at " + currentTime + " exceeding its deadline of " + deadline[taskId]);
        }
    }
}