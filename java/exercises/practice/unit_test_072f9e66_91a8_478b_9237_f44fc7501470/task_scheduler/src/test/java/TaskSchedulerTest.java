import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;

public class TaskSchedulerTest {

    @Test
    public void testEmptyTaskList() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resources = new HashMap<>();
        resources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, resources);
        
        assertTrue(schedule.isEmpty());
    }

    @Test
    public void testSingleTaskWithinDeadline() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        tasks.add(new Task("task1", 5, 10, new ArrayList<>(), resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertEquals(1, schedule.size());
        assertEquals("task1", schedule.get(0));
    }

    @Test
    public void testSingleTaskMissesDeadline() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        tasks.add(new Task("task1", 10, 5, new ArrayList<>(), resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertTrue(schedule.isEmpty());
    }

    @Test
    public void testMultipleTasksWithoutDependencies() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq1 = new HashMap<>();
        resourceReq1.put("CPU", 1);
        
        Map<String, Integer> resourceReq2 = new HashMap<>();
        resourceReq2.put("CPU", 1);
        
        tasks.add(new Task("task1", 5, 10, new ArrayList<>(), resourceReq1));
        tasks.add(new Task("task2", 3, 7, new ArrayList<>(), resourceReq2));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertEquals(2, schedule.size());
        assertEquals("task2", schedule.get(0)); // Shorter deadline first
        assertEquals("task1", schedule.get(1));
    }

    @Test
    public void testTasksWithSimpleDependencies() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        List<String> dependencies = new ArrayList<>();
        dependencies.add("task1");
        
        tasks.add(new Task("task1", 3, 10, new ArrayList<>(), resourceReq));
        tasks.add(new Task("task2", 4, 20, dependencies, resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertEquals(2, schedule.size());
        assertEquals("task1", schedule.get(0));
        assertEquals("task2", schedule.get(1));
    }

    @Test
    public void testTasksWithCircularDependencies() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        List<String> dependencies1 = new ArrayList<>();
        dependencies1.add("task2");
        
        List<String> dependencies2 = new ArrayList<>();
        dependencies2.add("task1");
        
        tasks.add(new Task("task1", 3, 10, dependencies1, resourceReq));
        tasks.add(new Task("task2", 4, 20, dependencies2, resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertTrue(schedule.isEmpty()); // Cannot schedule due to circular dependencies
    }

    @Test
    public void testTasksWithInsufficientResources() {
        List<Task> tasks = new ArrayList<>();
        
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 2);
        
        tasks.add(new Task("task1", 3, 10, new ArrayList<>(), resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertTrue(schedule.isEmpty()); // Cannot schedule due to insufficient resources
    }

    @Test
    public void testComplexTasksWithDependenciesAndResources() {
        List<Task> tasks = new ArrayList<>();
        
        // Create tasks
        Map<String, Integer> resourceReq1 = new HashMap<>();
        resourceReq1.put("CPU", 1);
        resourceReq1.put("Memory", 2);
        
        Map<String, Integer> resourceReq2 = new HashMap<>();
        resourceReq2.put("CPU", 1);
        resourceReq2.put("Memory", 1);
        
        Map<String, Integer> resourceReq3 = new HashMap<>();
        resourceReq3.put("CPU", 1);
        resourceReq3.put("Memory", 3);
        
        Map<String, Integer> resourceReq4 = new HashMap<>();
        resourceReq4.put("CPU", 1);
        resourceReq4.put("Memory", 1);
        resourceReq4.put("GPU", 1);
        
        // Define dependencies
        List<String> dependenciesForTask3 = new ArrayList<>();
        dependenciesForTask3.add("task1");
        
        List<String> dependenciesForTask4 = new ArrayList<>();
        dependenciesForTask4.add("task2");
        dependenciesForTask4.add("task3");
        
        // Add tasks
        tasks.add(new Task("task1", 3, 10, new ArrayList<>(), resourceReq1));
        tasks.add(new Task("task2", 2, 8, new ArrayList<>(), resourceReq2));
        tasks.add(new Task("task3", 4, 15, dependenciesForTask3, resourceReq3));
        tasks.add(new Task("task4", 2, 20, dependenciesForTask4, resourceReq4));
        
        // Define system resources
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        systemResources.put("Memory", 3);
        systemResources.put("GPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        // Expected schedule: task2, task1, task3, task4
        assertEquals(4, schedule.size());
        assertEquals("task2", schedule.get(0));
        assertEquals("task1", schedule.get(1));
        assertEquals("task3", schedule.get(2));
        assertEquals("task4", schedule.get(3));
    }

    @Test
    public void testPriorityOrderingWithIdenticalDeadlines() {
        List<Task> tasks = new ArrayList<>();
        
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        // Three tasks with identical deadlines but different execution times
        tasks.add(new Task("taskC", 5, 10, new ArrayList<>(), resourceReq));
        tasks.add(new Task("taskA", 2, 10, new ArrayList<>(), resourceReq));
        tasks.add(new Task("taskB", 3, 10, new ArrayList<>(), resourceReq));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        // Should prioritize by shorter execution time if deadlines are the same
        assertEquals(3, schedule.size());
        assertEquals("taskA", schedule.get(0)); // Shortest execution time
        assertEquals("taskB", schedule.get(1));
        assertEquals("taskC", schedule.get(2));
    }

    @Test
    public void testResourceReleaseAfterTaskCompletion() {
        List<Task> tasks = new ArrayList<>();
        
        // First task requires all memory
        Map<String, Integer> resourceReq1 = new HashMap<>();
        resourceReq1.put("Memory", 4);
        
        // Second task requires half memory
        Map<String, Integer> resourceReq2 = new HashMap<>();
        resourceReq2.put("Memory", 2);
        
        // Third task requires half memory
        Map<String, Integer> resourceReq3 = new HashMap<>();
        resourceReq3.put("Memory", 2);
        
        tasks.add(new Task("task1", 3, 10, new ArrayList<>(), resourceReq1));
        tasks.add(new Task("task2", 2, 15, new ArrayList<>(), resourceReq2));
        tasks.add(new Task("task3", 4, 20, new ArrayList<>(), resourceReq3));
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("Memory", 4);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        // Should be able to schedule all tasks as resources are released
        assertEquals(3, schedule.size());
        assertEquals("task1", schedule.get(0));
        // Task 2 and 3 could be in any order since they have sufficient resources after task1
        assertTrue(schedule.contains("task2"));
        assertTrue(schedule.contains("task3"));
    }

    @Test
    public void testLargeNumberOfTasks() {
        List<Task> tasks = new ArrayList<>();
        Random random = new Random(123); // Fixed seed for reproducibility
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 4);
        systemResources.put("Memory", 16);
        systemResources.put("GPU", 2);
        
        // Create 100 tasks with random properties but no dependencies
        for (int i = 0; i < 100; i++) {
            String taskId = "task" + i;
            int executionTime = 1 + random.nextInt(10);
            int deadline = executionTime + random.nextInt(20);
            
            Map<String, Integer> resourceReq = new HashMap<>();
            resourceReq.put("CPU", 1 + random.nextInt(2));
            resourceReq.put("Memory", 1 + random.nextInt(8));
            if (random.nextBoolean()) {
                resourceReq.put("GPU", 1);
            }
            
            tasks.add(new Task(taskId, executionTime, deadline, new ArrayList<>(), resourceReq));
        }
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        // Just verify we get a non-empty schedule - exact contents will depend on implementation
        assertFalse(schedule.isEmpty());
        // Verify no duplicates
        Set<String> uniqueTasks = new HashSet<>(schedule);
        assertEquals(schedule.size(), uniqueTasks.size());
    }

    @Test
    public void testComplexDependencyGraph() {
        List<Task> tasks = new ArrayList<>();
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        
        // Create tasks
        Task taskA = new Task("A", 2, 20, new ArrayList<>(), resourceReq);
        
        List<String> bDependencies = new ArrayList<>();
        bDependencies.add("A");
        Task taskB = new Task("B", 3, 25, bDependencies, resourceReq);
        
        List<String> cDependencies = new ArrayList<>();
        cDependencies.add("A");
        Task taskC = new Task("C", 2, 22, cDependencies, resourceReq);
        
        List<String> dDependencies = new ArrayList<>();
        dDependencies.add("B");
        dDependencies.add("C");
        Task taskD = new Task("D", 4, 30, dDependencies, resourceReq);
        
        List<String> eDependencies = new ArrayList<>();
        eDependencies.add("C");
        Task taskE = new Task("E", 1, 24, eDependencies, resourceReq);
        
        tasks.add(taskA);
        tasks.add(taskB);
        tasks.add(taskC);
        tasks.add(taskD);
        tasks.add(taskE);
        
        Map<String, Integer> systemResources = new HashMap<>();
        systemResources.put("CPU", 1);
        
        TaskScheduler scheduler = new TaskScheduler();
        List<String> schedule = scheduler.schedule(tasks, systemResources);
        
        assertEquals(5, schedule.size());
        
        // Verify dependencies are respected
        assertTrue(schedule.indexOf("A") < schedule.indexOf("B"));
        assertTrue(schedule.indexOf("A") < schedule.indexOf("C"));
        assertTrue(schedule.indexOf("B") < schedule.indexOf("D"));
        assertTrue(schedule.indexOf("C") < schedule.indexOf("D"));
        assertTrue(schedule.indexOf("C") < schedule.indexOf("E"));
    }
}