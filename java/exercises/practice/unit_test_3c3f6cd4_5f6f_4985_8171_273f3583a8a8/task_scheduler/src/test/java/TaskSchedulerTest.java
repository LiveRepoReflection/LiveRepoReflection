import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;

public class TaskSchedulerTest {

    // Helper method to create a list of dependencies from an array of int arrays.
    private List<List<Integer>> createDependencies(int[][] deps) {
        List<List<Integer>> dependencies = new ArrayList<>();
        for (int[] dep : deps) {
            List<Integer> list = new ArrayList<>();
            for (int d : dep) {
                list.add(d);
            }
            dependencies.add(list);
        }
        return dependencies;
    }

    @Test
    public void testSimpleSchedule() {
        // Example:
        // Task 0: duration 2, deadline 6, dependencies []
        // Task 1: duration 3, deadline 8, dependencies [0]
        // Task 2: duration 2, deadline 12, dependencies [1]
        int N = 3;
        int[] duration = {2, 3, 2};
        int[] deadline = {6, 8, 12};
        int[][] depsArray = {
            {},
            {0},
            {1}
        };
        List<List<Integer>> dependencies = createDependencies(depsArray);
        TaskScheduler scheduler = new TaskScheduler();
        // Expected maximum lateness is 0 (all tasks finish before their deadlines)
        int expected = 0;
        int result = scheduler.findMinMaxLateness(N, duration, deadline, dependencies);
        assertEquals(expected, result);
    }

    @Test
    public void testImpossibleScheduleSingleTask() {
        // Single task that cannot be finished within deadline.
        int N = 1;
        int[] duration = {5};
        int[] deadline = {3};
        int[][] depsArray = {
            {}
        };
        List<List<Integer>> dependencies = createDependencies(depsArray);
        TaskScheduler scheduler = new TaskScheduler();
        // It is impossible to finish task within its deadline, so expected is -1.
        int expected = -1;
        int result = scheduler.findMinMaxLateness(N, duration, deadline, dependencies);
        assertEquals(expected, result);
    }

    @Test
    public void testImpossibleScheduleParallelTasks() {
        // Two tasks that can be executed in any order (no dependencies) but deadlines are too tight when combined.
        int N = 2;
        int[] duration = {3, 4};
        int[] deadline = {3, 5};
        int[][] depsArray = {
            {},
            {}
        };
        List<List<Integer>> dependencies = createDependencies(depsArray);
        TaskScheduler scheduler = new TaskScheduler();
        // Even the optimal ordering cannot complete both tasks within their deadlines, so expected is -1.
        int expected = -1;
        int result = scheduler.findMinMaxLateness(N, duration, deadline, dependencies);
        assertEquals(expected, result);
    }

    @Test
    public void testComplexSchedule() {
        // Complex dependency scenario:
        // Task 0: duration 2, deadline 5, dependencies []
        // Task 1: duration 3, deadline 7, dependencies [0]
        // Task 2: duration 4, deadline 10, dependencies [0]
        // Task 3: duration 1, deadline 12, dependencies [1, 2]
        // Task 4: duration 2, deadline 15, dependencies [3]
        int N = 5;
        int[] duration = {2, 3, 4, 1, 2};
        int[] deadline = {5, 7, 10, 12, 15};
        int[][] depsArray = {
            {},
            {0},
            {0},
            {1, 2},
            {3}
        };
        List<List<Integer>> dependencies = createDependencies(depsArray);
        TaskScheduler scheduler = new TaskScheduler();
        // An optimal schedule finishes all tasks before their deadlines.
        int expected = 0;
        int result = scheduler.findMinMaxLateness(N, duration, deadline, dependencies);
        assertEquals(expected, result);
    }
}