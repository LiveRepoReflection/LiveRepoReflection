import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class TaskSchedulerTest {

    @Test
    public void testBasicAssignment() {
        int n = 2;
        List<int[]> tasks = Arrays.asList(
            new int[]{50, 100},
            new int[]{40, 120},
            new int[]{30, 150},
            new int[]{20, 200}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertEquals(tasks.size(), assignment.length);
        assertValidAssignment(n, assignment);
    }

    @Test
    public void testSingleWorker() {
        int n = 1;
        List<int[]> tasks = Arrays.asList(
            new int[]{10, 50},
            new int[]{20, 100},
            new int[]{30, 150}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertArrayEquals(new int[]{0, 0, 0}, assignment);
    }

    @Test
    public void testTightDeadlines() {
        int n = 3;
        List<int[]> tasks = Arrays.asList(
            new int[]{10, 15},
            new int[]{15, 20},
            new int[]{20, 25},
            new int[]{5, 10},
            new int[]{25, 30}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertEquals(tasks.size(), assignment.length);
        assertValidAssignment(n, assignment);
    }

    @Test
    public void testEqualTasks() {
        int n = 2;
        List<int[]> tasks = Arrays.asList(
            new int[]{10, 100},
            new int[]{10, 100},
            new int[]{10, 100},
            new int[]{10, 100}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertEquals(tasks.size(), assignment.length);
        assertValidAssignment(n, assignment);
    }

    @Test
    public void testMoreWorkersThanTasks() {
        int n = 5;
        List<int[]> tasks = Arrays.asList(
            new int[]{10, 50},
            new int[]{20, 100}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertEquals(tasks.size(), assignment.length);
        assertValidAssignment(n, assignment);
    }

    @Test
    public void testLargeNumberOfTasks() {
        int n = 4;
        List<int[]> tasks = Arrays.asList(
            new int[]{5, 50}, new int[]{8, 60}, new int[]{6, 70}, new int[]{7, 80},
            new int[]{10, 90}, new int[]{12, 100}, new int[]{15, 110}, new int[]{9, 120},
            new int[]{11, 130}, new int[]{13, 140}, new int[]{14, 150}, new int[]{16, 160}
        );
        
        TaskScheduler scheduler = new TaskScheduler();
        int[] assignment = scheduler.scheduleTasks(n, tasks);
        
        assertEquals(tasks.size(), assignment.length);
        assertValidAssignment(n, assignment);
    }

    private void assertValidAssignment(int n, int[] assignment) {
        for (int worker : assignment) {
            assertTrue(worker >= 0 && worker < n, "Invalid worker assignment");
        }
    }
}