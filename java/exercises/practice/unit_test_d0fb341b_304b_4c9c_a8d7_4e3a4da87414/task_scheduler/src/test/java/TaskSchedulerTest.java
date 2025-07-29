import org.junit.Test;
import org.junit.Before;
import static org.junit.Assert.*;
import java.util.*;

public class TaskSchedulerTest {
    private List<Task> tasks;

    @Before
    public void setUp() {
        tasks = new ArrayList<>();
    }

    @Test
    public void testNoDependencies() {
        tasks.add(new Task(1, 2, 5, new ArrayList<>()));
        tasks.add(new Task(2, 3, 8, new ArrayList<>()));
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertEquals(2, schedule.size());
        assertTrue(schedule.contains(1));
        assertTrue(schedule.contains(2));
    }

    @Test
    public void testWithDependencies() {
        tasks.add(new Task(1, 3, 7, new ArrayList<>()));
        tasks.add(new Task(2, 2, 5, Arrays.asList(1)));
        tasks.add(new Task(3, 4, 10, Arrays.asList(1, 2)));
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertEquals(3, schedule.size());
        assertEquals(1, (int)schedule.get(0));
        assertEquals(2, (int)schedule.get(1));
    }

    @Test
    public void testCircularDependencies() {
        tasks.add(new Task(1, 2, 5, Arrays.asList(3)));
        tasks.add(new Task(2, 3, 8, Arrays.asList(1)));
        tasks.add(new Task(3, 1, 6, Arrays.asList(2)));
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertTrue(schedule.isEmpty());
    }

    @Test
    public void testMissedDeadlines() {
        tasks.add(new Task(1, 5, 4, new ArrayList<>()));
        tasks.add(new Task(2, 2, 8, Arrays.asList(1)));
        tasks.add(new Task(3, 3, 12, new ArrayList<>()));
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertEquals(2, schedule.size());
        assertFalse(schedule.contains(1));
    }

    @Test
    public void testLargeNumberOfTasks() {
        for (int i = 1; i <= 1000; i++) {
            tasks.add(new Task(i, 1, i, new ArrayList<>()));
        }
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertEquals(1000, schedule.size());
        for (int i = 0; i < 1000; i++) {
            assertEquals(i + 1, (int)schedule.get(i));
        }
    }

    @Test
    public void testComplexDependencies() {
        tasks.add(new Task(1, 2, 5, new ArrayList<>()));
        tasks.add(new Task(2, 3, 10, Arrays.asList(1, 4)));
        tasks.add(new Task(3, 1, 15, Arrays.asList(2)));
        tasks.add(new Task(4, 2, 8, Arrays.asList(1)));
        tasks.add(new Task(5, 4, 20, Arrays.asList(3)));
        
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertEquals(5, schedule.size());
        assertEquals(1, (int)schedule.get(0));
        assertTrue(schedule.indexOf(4) < schedule.indexOf(2));
    }

    @Test
    public void testEmptyInput() {
        List<Integer> schedule = TaskScheduler.scheduleTasks(tasks);
        assertTrue(schedule.isEmpty());
    }
}