import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;

public class TaskSchedulerTest {

    @Test
    public void testChainZeroLateness() {
        int N = 3;
        int[] ids = {0, 1, 2};
        int[] durations = {2, 3, 2};
        int[] deadlines = {5, 7, 9};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());       // Task 0 has no dependencies
        dependencies.add(Arrays.asList(0));          // Task 1 depends on Task 0
        dependencies.add(Arrays.asList(1));          // Task 2 depends on Task 1

        int result = TaskScheduler.calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        assertEquals(0, result);
    }

    @Test
    public void testChainWithLateness() {
        int N = 3;
        int[] ids = {0, 1, 2};
        int[] durations = {2, 3, 2};
        int[] deadlines = {2, 3, 4}; // Deadlines are too early, expecting lateness
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        dependencies.add(Arrays.asList(0));
        dependencies.add(Arrays.asList(1));

        // Expected finish times: Task 0: 2, Task 1: 5, Task 2: 7.
        // Lateness: max(0,2-2)=0, max(0,5-3)=2, max(0,7-4)=3; total = 5.
        int result = TaskScheduler.calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        assertEquals(5, result);
    }

    @Test
    public void testNoDependencies() {
        int N = 2;
        int[] ids = {0, 1};
        int[] durations = {3, 2};
        int[] deadlines = {4, 2};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());       // Task 0 has no dependencies
        dependencies.add(new ArrayList<>());       // Task 1 has no dependencies

        // Optimal order is Task 1 then Task 0.
        // Completion times: Task 1: 2, Task 0: 2+3 = 5.
        // Lateness: Task 1: max(0,2-2)=0, Task 0: max(0,5-4)=1; total = 1.
        int result = TaskScheduler.calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        assertEquals(1, result);
    }

    @Test
    public void testDiamondDependencies() {
        int N = 4;
        int[] ids = {0, 1, 2, 3};
        int[] durations = {3, 2, 2, 4};
        int[] deadlines = {3, 8, 8, 15};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());          // Task 0
        dependencies.add(Arrays.asList(0));             // Task 1 depends on Task 0
        dependencies.add(Arrays.asList(0));             // Task 2 depends on Task 0
        dependencies.add(Arrays.asList(1, 2));            // Task 3 depends on Task 1 and Task 2

        // One possible optimal schedule: Task 0, Task 1, Task 2, Task 3.
        // Expected finish times: 3, 5, 7, 11, all within deadlines.
        int result = TaskScheduler.calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        assertEquals(0, result);
    }

    @Test
    public void testNoDependenciesStrictDeadlines() {
        int N = 2;
        int[] ids = {0, 1};
        int[] durations = {8, 3};
        int[] deadlines = {5, 5};
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());      // Task 0
        dependencies.add(new ArrayList<>());      // Task 1

        // Optimal order is Task 1 then Task 0.
        // Completion times: Task 1: 3, Task 0: 3+8 = 11.
        // Lateness: Task 1: max(0,3-5)=0, Task 0: max(0,11-5)=6; total = 6.
        int result = TaskScheduler.calculateMinimumLateness(N, ids, durations, deadlines, dependencies);
        assertEquals(6, result);
    }
}