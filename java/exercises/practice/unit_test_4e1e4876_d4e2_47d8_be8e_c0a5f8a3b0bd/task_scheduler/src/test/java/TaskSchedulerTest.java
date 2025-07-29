package task_scheduler;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    @Test
    public void testSimpleChain() {
        int n = 4;
        int[][] dependencies = { {0, 1}, {1, 2}, {2, 3} };
        int resources = 10;
        int[] taskResources = {2, 2, 2, 2};
        int[] taskExecutionTimes = {1, 2, 3, 4};
        
        // Tasks must run sequentially due to chain dependencies.
        // Expected makespan = 1 + 2 + 3 + 4 = 10.
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        assertEquals(10, result);
    }
    
    @Test
    public void testIndependentTasksParallel() {
        int n = 3;
        int[][] dependencies = {};
        int resources = 10;
        int[] taskResources = {3, 3, 3};
        int[] taskExecutionTimes = {4, 4, 4};
        
        // All tasks are independent and can run in parallel.
        // Expected makespan = maximum execution time among tasks = 4.
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        assertEquals(4, result);
    }
    
    @Test
    public void testResourceConstraintSerial() {
        int n = 4;
        int[][] dependencies = {};
        int resources = 5;
        int[] taskResources = {5, 5, 5, 5};
        int[] taskExecutionTimes = {2, 3, 1, 4};
        
        // Even though there are no dependencies, each task requires all resources.
        // Thus tasks must execute sequentially and makespan = 2 + 3 + 1 + 4 = 10.
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        assertEquals(10, result);
    }
    
    @Test
    public void testComplexGraph() {
        int n = 6;
        int[][] dependencies = {
            {0, 2},
            {1, 2},
            {1, 3},
            {2, 4},
            {3, 4},
            {4, 5}
        };
        int resources = 7;
        int[] taskResources = {3, 2, 4, 1, 3, 2};
        int[] taskExecutionTimes = {2, 3, 4, 2, 1, 5};
        
        // Expected scheduling:
        // - Tasks 0 and 1 start at time 0, finish at time 2 and 3 respectively.
        // - Task 2 waits until both 0 and 1 are complete, starting at time 3 and finishing at time 7.
        // - Task 3 can start at time 3 (after task1 completes) and finish at time 5.
        // - Task 4 waits for tasks 2 and 3 to complete, starting at time 7 and finishing at time 8.
        // - Task 5 then starts at time 8 and finishes at time 13.
        // Expected makespan = 13.
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        assertEquals(13, result);
    }
    
    @Test
    public void testEdgeLargeResourceAvailability() {
        int n = 5;
        int[][] dependencies = { {0, 1}, {0, 2}, {1, 3}, {2, 4} };
        int resources = 100;
        int[] taskResources = {5, 5, 5, 5, 5};
        int[] taskExecutionTimes = {3, 2, 2, 4, 4};
        
        // With abundant resources, tasks can run concurrently if dependencies allow.
        // Scheduling:
        // - Task 0 runs at time 0; finishes at time 3.
        // - Tasks 1 and 2 start at time 3; finish at time 5.
        // - Task 3 (dependent on 1) and Task 4 (dependent on 2) start at time 5; finish at time 9.
        // Expected makespan = 9.
        TaskScheduler scheduler = new TaskScheduler();
        int result = scheduler.schedule(n, dependencies, resources, taskResources, taskExecutionTimes);
        assertEquals(9, result);
    }
}