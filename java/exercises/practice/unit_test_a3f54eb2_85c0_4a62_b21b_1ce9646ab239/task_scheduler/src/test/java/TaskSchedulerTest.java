import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {
    private TaskScheduler scheduler;

    @BeforeEach
    public void setUp() {
        scheduler = new TaskScheduler();
    }

    @Test
    public void testEmptyTaskList() {
        List<Task> tasks = new ArrayList<>();
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertTrue(result.isEmpty());
    }

    @Test
    public void testEmptyWorkerList() {
        List<Task> tasks = Arrays.asList(new Task(0, 10.0, 20.0, new ArrayList<>()));
        List<Worker> workers = new ArrayList<>();
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertTrue(result.isEmpty());
    }

    @Test
    public void testSingleTaskSingleWorker() {
        List<Task> tasks = Arrays.asList(new Task(0, 10.0, 20.0, new ArrayList<>()));
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(1, result.size());
        assertEquals(0, result.get(0).taskId);
        assertEquals(0, result.get(0).workerId);
        assertEquals(0, result.get(0).startTime);
        assertEquals(10.0, result.get(0).endTime);
    }

    @Test
    public void testMultipleTasksNoOverlap() {
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 20.0, new ArrayList<>()),
            new Task(1, 20.0, 50.0, new ArrayList<>()),
            new Task(2, 15.0, 100.0, new ArrayList<>())
        );
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(3, result.size());
        assertTrue(result.stream().anyMatch(a -> a.taskId == 0));
        assertTrue(result.stream().anyMatch(a -> a.taskId == 1));
        assertTrue(result.stream().anyMatch(a -> a.taskId == 2));
        
        // Verify no overlaps
        for (int i = 0; i < result.size(); i++) {
            for (int j = i + 1; j < result.size(); j++) {
                if (result.get(i).workerId == result.get(j).workerId) {
                    assertFalse((result.get(i).startTime <= result.get(j).startTime && 
                                result.get(i).endTime > result.get(j).startTime) ||
                               (result.get(j).startTime <= result.get(i).startTime && 
                                result.get(j).endTime > result.get(i).startTime));
                }
            }
        }
    }

    @Test
    public void testTasksWithDependencies() {
        List<Integer> dependencies = new ArrayList<>();
        dependencies.add(0);
        
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 20.0, new ArrayList<>()),
            new Task(1, 15.0, 50.0, dependencies)
        );
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(2, result.size());
        
        // Find assignments for each task
        Assignment task0Assignment = null;
        Assignment task1Assignment = null;
        
        for (Assignment a : result) {
            if (a.taskId == 0) task0Assignment = a;
            if (a.taskId == 1) task1Assignment = a;
        }
        
        assertNotNull(task0Assignment);
        assertNotNull(task1Assignment);
        
        // Verify dependency constraint
        assertTrue(task0Assignment.endTime <= task1Assignment.startTime);
    }

    @Test
    public void testMultipleWorkers() {
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 10.0, new ArrayList<>()),
            new Task(1, 10.0, 10.0, new ArrayList<>())
        );
        List<Worker> workers = Arrays.asList(
            new Worker(0, 1.0),
            new Worker(1, 1.0)
        );
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(2, result.size());
        
        // Both tasks should be scheduled in parallel
        Assignment assignment1 = result.stream().filter(a -> a.taskId == 0).findFirst().orElse(null);
        Assignment assignment2 = result.stream().filter(a -> a.taskId == 1).findFirst().orElse(null);
        
        assertNotNull(assignment1);
        assertNotNull(assignment2);
        
        // Verify they are on different workers
        assertNotEquals(assignment1.workerId, assignment2.workerId);
    }

    @Test
    public void testDifferentWorkerCapabilities() {
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 10.0, new ArrayList<>())
        );
        List<Worker> workers = Arrays.asList(
            new Worker(0, 2.0)  // 2x faster
        );
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(1, result.size());
        Assignment assignment = result.get(0);
        assertEquals(0, assignment.taskId);
        assertEquals(0, assignment.workerId);
        
        // Processing time should be halved due to worker capability
        assertEquals(5.0, assignment.endTime - assignment.startTime);
    }

    @Test
    public void testComplexDependencies() {
        // Task 0 -> Task 1 -> Task 3
        //       \-> Task 2 -/
        
        List<Integer> dep1 = new ArrayList<>();
        dep1.add(0);
        
        List<Integer> dep2 = new ArrayList<>();
        dep2.add(0);
        
        List<Integer> dep3 = new ArrayList<>();
        dep3.add(1);
        dep3.add(2);
        
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 100.0, new ArrayList<>()),
            new Task(1, 15.0, 100.0, dep1),
            new Task(2, 20.0, 100.0, dep2),
            new Task(3, 10.0, 100.0, dep3)
        );
        
        List<Worker> workers = Arrays.asList(
            new Worker(0, 1.0),
            new Worker(1, 1.0)
        );
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(4, result.size());
        
        // Find assignments for each task
        Map<Integer, Assignment> assignmentMap = new HashMap<>();
        for (Assignment a : result) {
            assignmentMap.put(a.taskId, a);
        }
        
        // Verify dependency constraints
        assertTrue(assignmentMap.get(0).endTime <= assignmentMap.get(1).startTime);
        assertTrue(assignmentMap.get(0).endTime <= assignmentMap.get(2).startTime);
        assertTrue(assignmentMap.get(1).endTime <= assignmentMap.get(3).startTime);
        assertTrue(assignmentMap.get(2).endTime <= assignmentMap.get(3).startTime);
    }

    @Test
    public void testImpossibleDeadline() {
        List<Task> tasks = Arrays.asList(
            new Task(0, 100.0, 10.0, new ArrayList<>())  // Can't complete in time
        );
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertTrue(result.isEmpty());
    }

    @Test
    public void testOptimalResourceAllocation() {
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 10.0, new ArrayList<>()),
            new Task(1, 20.0, 20.0, new ArrayList<>())
        );
        List<Worker> workers = Arrays.asList(
            new Worker(0, 1.0),
            new Worker(1, 5.0)  // 5x faster
        );
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(2, result.size());
        
        // Verify the longer task is assigned to the faster worker
        Assignment task0Assignment = null;
        Assignment task1Assignment = null;
        
        for (Assignment a : result) {
            if (a.taskId == 0) task0Assignment = a;
            if (a.taskId == 1) task1Assignment = a;
        }
        
        assertNotNull(task0Assignment);
        assertNotNull(task1Assignment);
        
        // The task with longer processing time should be assigned to the faster worker
        assertEquals(1, task1Assignment.workerId);
    }

    @Test
    public void testLargeInputScalability() {
        List<Task> tasks = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            List<Integer> dependencies = new ArrayList<>();
            if (i > 0) dependencies.add(i-1);
            tasks.add(new Task(i, 10.0, 1000.0, dependencies));
        }
        
        List<Worker> workers = new ArrayList<>();
        for (int i = 0; i < 10; i++) {
            workers.add(new Worker(i, 1.0 + (i * 0.5)));
        }
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        assertEquals(50, result.size());
        
        // Check that all tasks are assigned
        Set<Integer> assignedTasks = new HashSet<>();
        for (Assignment a : result) {
            assignedTasks.add(a.taskId);
        }
        assertEquals(50, assignedTasks.size());
        
        // Verify dependency order
        Map<Integer, Assignment> assignmentMap = new HashMap<>();
        for (Assignment a : result) {
            assignmentMap.put(a.taskId, a);
        }
        
        for (int i = 1; i < 50; i++) {
            assertTrue(assignmentMap.get(i-1).endTime <= assignmentMap.get(i).startTime);
        }
    }
    
    @Test
    public void testCircularDependencies() {
        List<Integer> dep1 = new ArrayList<>();
        dep1.add(1);  // Task 0 depends on Task 1
        
        List<Integer> dep2 = new ArrayList<>();
        dep2.add(0);  // Task 1 depends on Task 0 - circular!
        
        List<Task> tasks = Arrays.asList(
            new Task(0, 10.0, 100.0, dep1),
            new Task(1, 15.0, 100.0, dep2)
        );
        
        List<Worker> workers = Arrays.asList(new Worker(0, 1.0));
        
        List<Assignment> result = scheduler.scheduleTasksOptimally(tasks, workers);
        
        // Should detect circular dependency and return empty list
        assertTrue(result.isEmpty());
    }
}