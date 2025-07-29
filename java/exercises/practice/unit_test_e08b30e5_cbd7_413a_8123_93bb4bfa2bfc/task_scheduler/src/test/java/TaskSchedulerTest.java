package task_scheduler;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;

public class TaskSchedulerTest {

    private TaskScheduler scheduler;

    @BeforeEach
    public void setup() {
        scheduler = new TaskScheduler();
    }

    @Test
    public void testNoMissedDeadlines() {
        int N = 3;
        int K = 2;
        int[] taskIds = new int[]{1, 2, 3};
        int[] executionTime = new int[]{50, 50, 50};
        int[] deadlines = new int[]{200, 200, 200};
        
        // No dependencies for any task
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());
        dependencies.add(new ArrayList<>());
        dependencies.add(new ArrayList<>());

        List<Integer> result = scheduler.scheduleTasks(N, K, taskIds, executionTime, deadlines, dependencies);
        // Expect no missed deadlines.
        assertTrue(result.isEmpty());
    }
    
    @Test
    public void testMissedDeadlines() {
        int N = 5;
        int K = 2;
        int[] taskIds = new int[]{1, 2, 3, 4, 5};
        int[] executionTime = new int[]{100, 50, 75, 25, 125};
        int[] deadlines = new int[]{200, 150, 250, 100, 300};

        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());           // Task 1: no dependencies
        dependencies.add(Arrays.asList(1));              // Task 2: depends on Task 1
        dependencies.add(Arrays.asList(2));              // Task 3: depends on Task 2
        dependencies.add(Arrays.asList(1, 2));             // Task 4: depends on Task 1 and Task 2
        dependencies.add(Arrays.asList(3, 4));             // Task 5: depends on Task 3 and Task 4

        List<Integer> result = scheduler.scheduleTasks(N, K, taskIds, executionTime, deadlines, dependencies);
        // Expected result based on sample heuristic. The expected missed deadlines are tasks 4 and 5.
        List<Integer> expectedMissed = Arrays.asList(4, 5);
        assertEquals(expectedMissed, result);
    }
    
    @Test
    public void testCyclicDependencyDetection() {
        int N = 3;
        int K = 1;
        int[] taskIds = new int[]{1, 2, 3};
        int[] executionTime = new int[]{100, 100, 100};
        int[] deadlines = new int[]{300, 300, 300};

        // Create a cyclic dependency: 1 -> 2 -> 3 -> 1
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(Arrays.asList(2));   // Task 1 depends on Task 2
        dependencies.add(Arrays.asList(3));   // Task 2 depends on Task 3
        dependencies.add(Arrays.asList(1));   // Task 3 depends on Task 1

        assertThrows(CyclicDependencyException.class, () -> {
            scheduler.scheduleTasks(N, K, taskIds, executionTime, deadlines, dependencies);
        });
    }
    
    @Test
    public void testInvalidDependenciesIgnored() {
        int N = 3;
        int K = 2;
        int[] taskIds = new int[]{1, 2, 3};
        int[] executionTime = new int[]{60, 60, 60};
        int[] deadlines = new int[]{150, 150, 150};

        // Task 2 has an invalid dependency 99, which does not exist in taskIds.
        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());              // Task 1: no dependencies
        dependencies.add(Arrays.asList(1, 99));             // Task 2: valid dependency 1 and invalid dependency 99
        dependencies.add(Arrays.asList(1));                 // Task 3: depends on Task 1

        List<Integer> result = scheduler.scheduleTasks(N, K, taskIds, executionTime, deadlines, dependencies);
        // Expect no missed deadlines since invalid dependencies are ignored.
        assertTrue(result.isEmpty());
    }
    
    @Test
    public void testZeroExecutionTimeTasks() {
        int N = 4;
        int K = 2;
        int[] taskIds = new int[]{1, 2, 3, 4};
        int[] executionTime = new int[]{0, 50, 0, 100};
        int[] deadlines = new int[]{100, 150, 100, 200};

        List<List<Integer>> dependencies = new ArrayList<>();
        dependencies.add(new ArrayList<>());             // Task 1: execution time 0
        dependencies.add(Arrays.asList(1));                // Task 2: depends on Task 1
        dependencies.add(new ArrayList<>());               // Task 3: execution time 0
        dependencies.add(Arrays.asList(3));                // Task 4: depends on Task 3

        List<Integer> result = scheduler.scheduleTasks(N, K, taskIds, executionTime, deadlines, dependencies);
        // Expect no missed deadlines, ensuring zero execution time tasks do not block scheduling.
        assertTrue(result.isEmpty());
    }
}