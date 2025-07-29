import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.HashMap;
import java.util.Map;

public class TaskSchedulerTest {
    private TaskScheduler scheduler;
    private WorkerNode worker1, worker2;
    private Task task1, task2, task3;

    @BeforeEach
    public void setUp() {
        scheduler = new TaskScheduler();
        
        Map<String, Integer> resources1 = new HashMap<>();
        resources1.put("CPU", 4);
        resources1.put("Memory", 16);
        worker1 = new WorkerNode("worker1", resources1);
        
        Map<String, Integer> resources2 = new HashMap<>();
        resources2.put("CPU", 8);
        resources2.put("Memory", 32);
        worker2 = new WorkerNode("worker2", resources2);
        
        scheduler.addWorkerNode(worker1);
        scheduler.addWorkerNode(worker2);
        
        Map<String, Integer> req1 = new HashMap<>();
        req1.put("CPU", 2);
        req1.put("Memory", 8);
        task1 = new Task("task1", 1, 1000L, req1);
        
        Map<String, Integer> req2 = new HashMap<>();
        req2.put("CPU", 4);
        req2.put("Memory", 16);
        task2 = new Task("task2", 2, 2000L, req2);
        
        Map<String, Integer> req3 = new HashMap<>();
        req3.put("CPU", 1);
        req3.put("Memory", 4);
        task3 = new Task("task3", 3, 3000L, req3);
    }

    @Test
    public void testTaskAssignmentWithSufficientResources() {
        assertTrue(scheduler.scheduleTask(task1));
        assertTrue(scheduler.scheduleTask(task2));
    }

    @Test
    public void testTaskAssignmentWithInsufficientResources() {
        Map<String, Integer> largeReq = new HashMap<>();
        largeReq.put("CPU", 16);
        largeReq.put("Memory", 64);
        Task largeTask = new Task("largeTask", 1, 1000L, largeReq);
        
        assertFalse(scheduler.scheduleTask(largeTask));
    }

    @Test
    public void testTaskDeadlineViolation() {
        Task urgentTask = new Task("urgentTask", 1, 1L, 
            Map.of("CPU", 1, "Memory", 1));
        
        // Simulate all workers busy
        worker1.setCurrentResourceAllocation(worker1.getResourceCapacity());
        worker2.setCurrentResourceAllocation(worker2.getResourceCapacity());
        
        assertFalse(scheduler.scheduleTask(urgentTask));
    }

    @Test
    public void testResourceReleaseAfterTaskCompletion() {
        scheduler.scheduleTask(task1);
        scheduler.scheduleTask(task2);
        
        scheduler.taskCompleted("task1");
        
        // Should now be able to schedule task3
        assertTrue(scheduler.scheduleTask(task3));
    }

    @Test
    public void testWorkerNodeRemoval() {
        scheduler.scheduleTask(task1);
        scheduler.removeWorkerNode("worker1");
        
        // Task1 should be rescheduled to worker2 if possible
        assertTrue(worker2.getCurrentResourceAllocation().get("CPU") > 0);
    }

    @Test
    public void testTaskCancellation() {
        scheduler.scheduleTask(task1);
        scheduler.scheduleTask(task2);
        
        scheduler.cancelTask("task1");
        
        // Resources should be freed up
        assertTrue(scheduler.scheduleTask(task3));
    }

    @Test
    public void testPriorityBasedScheduling() {
        Task highPriorityTask = new Task("hpTask", 0, 1000L, 
            Map.of("CPU", 2, "Memory", 8));
        
        scheduler.scheduleTask(task1);
        scheduler.scheduleTask(highPriorityTask);
        
        // High priority task should preempt if necessary
        assertTrue(worker1.getCurrentResourceAllocation().get("CPU") >= 2);
    }

    @Test
    public void testConcurrentTaskSubmission() throws InterruptedException {
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 100; i++) {
                scheduler.scheduleTask(new Task("t1-" + i, 1, 1000L, 
                    Map.of("CPU", 1, "Memory", 2)));
            }
        });
        
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 100; i++) {
                scheduler.scheduleTask(new Task("t2-" + i, 1, 1000L, 
                    Map.of("CPU", 1, "Memory", 2)));
            }
        });
        
        t1.start();
        t2.start();
        t1.join();
        t2.join();
        
        // Verify no resource leaks
        int totalCPU = worker1.getResourceCapacity().get("CPU") + 
                      worker2.getResourceCapacity().get("CPU");
        int usedCPU = worker1.getCurrentResourceAllocation().get("CPU") + 
                     worker2.getCurrentResourceAllocation().get("CPU");
        
        assertTrue(usedCPU <= totalCPU);
    }
}