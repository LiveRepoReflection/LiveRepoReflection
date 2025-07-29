import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.HashMap;
import java.util.Map;

public class ResourceAllocatorTest {
    
    @Test
    public void testBasicAllocation() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 8);
        initialResources.put("Memory", 16);
        initialResources.put("Disk", 100);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        Map<String, Integer> taskRequirements = new HashMap<>();
        taskRequirements.put("CPU", 2);
        taskRequirements.put("Memory", 4);
        
        boolean result = allocator.allocateResources("task1", 1, taskRequirements, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        assertTrue(result);
        assertEquals(6, allocator.getAvailableResources().get("CPU"));
        assertEquals(12, allocator.getAvailableResources().get("Memory"));
    }

    @Test
    public void testInsufficientResources() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 2);
        initialResources.put("Memory", 4);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        Map<String, Integer> taskRequirements = new HashMap<>();
        taskRequirements.put("CPU", 4);
        taskRequirements.put("Memory", 8);
        
        boolean result = allocator.allocateResources("task2", 2, taskRequirements, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        assertFalse(result);
        assertEquals(2, allocator.getAvailableResources().get("CPU"));
        assertEquals(4, allocator.getAvailableResources().get("Memory"));
    }

    @Test
    public void testDeadlineMissed() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 8);
        initialResources.put("Memory", 16);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        Map<String, Integer> taskRequirements = new HashMap<>();
        taskRequirements.put("CPU", 2);
        taskRequirements.put("Memory", 4);
        
        boolean result = allocator.allocateResources("task3", 3, taskRequirements, 
            System.currentTimeMillis() - 20000, System.currentTimeMillis() - 10000, 5000);
        
        assertFalse(result);
    }

    @Test
    public void testResourceRelease() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 8);
        initialResources.put("Memory", 16);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        Map<String, Integer> taskRequirements = new HashMap<>();
        taskRequirements.put("CPU", 2);
        taskRequirements.put("Memory", 4);
        
        allocator.allocateResources("task4", 4, taskRequirements, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        allocator.releaseResources("task4");
        
        assertEquals(8, allocator.getAvailableResources().get("CPU"));
        assertEquals(16, allocator.getAvailableResources().get("Memory"));
    }

    @Test
    public void testPriorityPreemption() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 4);
        initialResources.put("Memory", 8);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        // Allocate lower priority task first
        Map<String, Integer> lowPriorityReq = new HashMap<>();
        lowPriorityReq.put("CPU", 2);
        lowPriorityReq.put("Memory", 4);
        allocator.allocateResources("lowTask", 1, lowPriorityReq, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        // Try to allocate higher priority task
        Map<String, Integer> highPriorityReq = new HashMap<>();
        highPriorityReq.put("CPU", 4);
        highPriorityReq.put("Memory", 8);
        boolean result = allocator.allocateResources("highTask", 5, highPriorityReq, 
            System.currentTimeMillis(), System.currentTimeMillis() + 5000, 3000);
        
        assertTrue(result);
        assertFalse(allocator.isTaskActive("lowTask"));
    }

    @Test
    public void testFragmentationHandling() {
        Map<String, Integer> initialResources = new HashMap<>();
        initialResources.put("CPU", 8);
        initialResources.put("Memory", 16);
        
        ResourceAllocator allocator = new ResourceAllocator(initialResources);
        
        // Allocate small chunks
        Map<String, Integer> smallReq1 = new HashMap<>();
        smallReq1.put("CPU", 1);
        smallReq1.put("Memory", 2);
        allocator.allocateResources("small1", 1, smallReq1, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        Map<String, Integer> smallReq2 = new HashMap<>();
        smallReq2.put("CPU", 1);
        smallReq2.put("Memory", 2);
        allocator.allocateResources("small2", 1, smallReq2, 
            System.currentTimeMillis(), System.currentTimeMillis() + 10000, 5000);
        
        // Try to allocate large task
        Map<String, Integer> largeReq = new HashMap<>();
        largeReq.put("CPU", 6);
        largeReq.put("Memory", 12);
        boolean result = allocator.allocateResources("largeTask", 2, largeReq, 
            System.currentTimeMillis(), System.currentTimeMillis() + 5000, 3000);
        
        assertTrue(result);
        assertEquals(0, allocator.getAvailableResources().get("CPU"));
        assertEquals(0, allocator.getAvailableResources().get("Memory"));
    }
}