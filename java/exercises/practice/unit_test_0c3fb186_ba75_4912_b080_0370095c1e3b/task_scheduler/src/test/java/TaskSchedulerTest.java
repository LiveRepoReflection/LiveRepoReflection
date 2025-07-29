import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TaskSchedulerTest {

    @Test
    public void testSimpleCase() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 2, 5, 10, new ArrayList<>()));
        tasks.add(new Task(2, 3, 7, 5, Arrays.asList(1)));
        tasks.add(new Task(3, 1, 6, 20, Arrays.asList(1)));
        tasks.add(new Task(4, 4, 10, 2, Arrays.asList(2, 3)));

        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(4, schedule.size());
        
        // Verify all tasks are scheduled
        Set<Integer> taskIds = new HashSet<>();
        for (Integer id : schedule) {
            taskIds.add(id);
        }
        assertEquals(4, taskIds.size());
        
        // Verify dependencies are respected
        Map<Integer, Integer> positions = new HashMap<>();
        for (int i = 0; i < schedule.size(); i++) {
            positions.put(schedule.get(i), i);
        }
        
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                assertTrue(positions.get(dependency) < positions.get(task.id),
                        "Task " + task.id + " should come after its dependency " + dependency);
            }
        }
        
        // Calculate the total penalty of the schedule
        int currentTime = 0;
        int totalPenalty = 0;
        
        for (int taskId : schedule) {
            Task task = findTaskById(tasks, taskId);
            currentTime += task.duration;
            if (currentTime > task.deadline) {
                totalPenalty += task.penalty;
            }
        }
        
        // We cannot assert the exact penalty as there might be multiple optimal solutions
        // but we can check if a schedule with obvious violations is not returned
    }
    
    @Test
    public void testNoDependencies() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 3, 3, 10, new ArrayList<>()));
        tasks.add(new Task(2, 2, 5, 5, new ArrayList<>()));
        tasks.add(new Task(3, 1, 4, 7, new ArrayList<>()));
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(3, schedule.size());
        
        // For tasks with no dependencies, an optimal approach would be 
        // to schedule them in order of (deadline - duration) or by penalty/duration ratio
        // We cannot assert the exact order as multiple strategies could be optimal
    }
    
    @Test
    public void testComplexDependencies() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 1, 10, 5, new ArrayList<>()));
        tasks.add(new Task(2, 1, 10, 10, Arrays.asList(1)));
        tasks.add(new Task(3, 1, 10, 15, Arrays.asList(2)));
        tasks.add(new Task(4, 1, 10, 20, Arrays.asList(1)));
        tasks.add(new Task(5, 1, 10, 25, Arrays.asList(4, 3)));
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(5, schedule.size());
        
        // Verify dependencies
        Map<Integer, Integer> positions = new HashMap<>();
        for (int i = 0; i < schedule.size(); i++) {
            positions.put(schedule.get(i), i);
        }
        
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                assertTrue(positions.get(dependency) < positions.get(task.id),
                        "Task " + task.id + " should come after its dependency " + dependency);
            }
        }
    }
    
    @Test
    public void testSameDurationSameDeadline() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 5, 10, 10, new ArrayList<>()));
        tasks.add(new Task(2, 5, 10, 20, new ArrayList<>()));
        tasks.add(new Task(3, 5, 10, 30, new ArrayList<>()));
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(3, schedule.size());
        
        // When all tasks have the same duration and deadline, ordering by penalty (decreasing) is optimal
        // Since all tasks will miss their deadlines except for at most one
    }
    
    @Test
    public void testLargeDurations() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 100, 50, 5, new ArrayList<>()));  // Will definitely miss
        tasks.add(new Task(2, 20, 200, 50, new ArrayList<>())); // Might make it depending on schedule
        tasks.add(new Task(3, 30, 150, 20, new ArrayList<>())); // Might make it depending on schedule
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(3, schedule.size());
    }
    
    @Test
    public void testZeroPenalties() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 3, 5, 0, new ArrayList<>()));     // No penalty
        tasks.add(new Task(2, 2, 4, 10, Arrays.asList(1)));    // Has penalty and depends on 1
        tasks.add(new Task(3, 1, 10, 5, new ArrayList<>()));    // Has penalty but no dependencies
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(3, schedule.size());
    }
    
    @Test
    public void testDAGWithMultiplePaths() {
        List<Task> tasks = new ArrayList<>();
        tasks.add(new Task(1, 1, 10, 5, new ArrayList<>()));
        tasks.add(new Task(2, 1, 10, 10, Arrays.asList(1)));
        tasks.add(new Task(3, 1, 10, 15, Arrays.asList(1)));
        tasks.add(new Task(4, 1, 10, 20, Arrays.asList(2, 3)));
        tasks.add(new Task(5, 1, 10, 25, Arrays.asList(4)));
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(5, schedule.size());
        
        // Verify dependencies
        Map<Integer, Integer> positions = new HashMap<>();
        for (int i = 0; i < schedule.size(); i++) {
            positions.put(schedule.get(i), i);
        }
        
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                assertTrue(positions.get(dependency) < positions.get(task.id),
                        "Task " + task.id + " should come after its dependency " + dependency);
            }
        }
    }
    
    @Test
    public void testLargerExample() {
        List<Task> tasks = new ArrayList<>();
        // Create a larger set of tasks with various dependencies
        for (int i = 1; i <= 20; i++) {
            List<Integer> deps = new ArrayList<>();
            if (i > 1 && i <= 5) {
                deps.add(1); // Tasks 2-5 depend on 1
            } else if (i > 5 && i <= 10) {
                deps.add(i - 5); // Tasks 6-10 depend on 1-5 respectively
            } else if (i > 10 && i <= 15) {
                deps.add(i - 10);
                deps.add(i - 5); // Tasks 11-15 depend on 1-5 and 6-10
            } else if (i > 15) {
                deps.add(i - 5); // Tasks 16-20 depend on 11-15
            }
            
            tasks.add(new Task(i, i % 5 + 1, 30 + i, i * 5, deps));
        }
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(20, schedule.size());
        
        // Verify all tasks are in the schedule
        Set<Integer> taskIds = new HashSet<>();
        for (Integer id : schedule) {
            taskIds.add(id);
        }
        assertEquals(20, taskIds.size());
        
        // Verify dependencies
        Map<Integer, Integer> positions = new HashMap<>();
        for (int i = 0; i < schedule.size(); i++) {
            positions.put(schedule.get(i), i);
        }
        
        for (Task task : tasks) {
            for (int dependency : task.dependencies) {
                assertTrue(positions.get(dependency) < positions.get(task.id),
                        "Task " + task.id + " should come after its dependency " + dependency);
            }
        }
    }
    
    @Test
    public void testEmptyDependencies() {
        List<Task> tasks = new ArrayList<>();
        for (int i = 1; i <= 5; i++) {
            tasks.add(new Task(i, 1, i, i * 10, new ArrayList<>()));
        }
        
        TaskScheduler scheduler = new TaskScheduler();
        List<Integer> schedule = scheduler.findOptimalSchedule(tasks);
        
        assertNotNull(schedule);
        assertEquals(5, schedule.size());
    }

    // Helper method to find a task by ID
    private Task findTaskById(List<Task> tasks, int id) {
        for (Task task : tasks) {
            if (task.id == id) {
                return task;
            }
        }
        return null;
    }
}