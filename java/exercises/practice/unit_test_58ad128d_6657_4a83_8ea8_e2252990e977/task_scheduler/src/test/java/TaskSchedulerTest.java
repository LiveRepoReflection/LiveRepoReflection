import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;
import java.util.*;

public class TaskSchedulerTest {
    @Test
    public void testSimpleScheduling() {
        // Create a simple task
        Map<String, Integer> resourceReq1 = new HashMap<>();
        resourceReq1.put("CPU", 2);
        resourceReq1.put("Memory", 4);
        
        Task task1 = new Task("task1", resourceReq1, 100L, 1, new HashSet<>());
        
        // Create a machine with sufficient resources
        Map<String, Integer> machineRes1 = new HashMap<>();
        machineRes1.put("CPU", 4);
        machineRes1.put("Memory", 8);
        
        Machine machine1 = new Machine("machine1", machineRes1, "US-East");
        
        // Create network cost matrix
        int[][] networkCost = new int[][]{{0}};
        
        TaskScheduler scheduler = new TaskScheduler();
        Map<String, String> schedule = scheduler.schedule(
            Arrays.asList(task1),
            Arrays.asList(machine1),
            networkCost
        );
        
        assertThat(schedule).containsEntry("task1", "machine1");
    }
    
    @Test
    public void testInsufficientResources() {
        // Create a task with high resource requirements
        Map<String, Integer> resourceReq1 = new HashMap<>();
        resourceReq1.put("CPU", 8);
        resourceReq1.put("Memory", 16);
        
        Task task1 = new Task("task1", resourceReq1, 100L, 1, new HashSet<>());
        
        // Create a machine with insufficient resources
        Map<String, Integer> machineRes1 = new HashMap<>();
        machineRes1.put("CPU", 2);
        machineRes1.put("Memory", 4);
        
        Machine machine1 = new Machine("machine1", machineRes1, "US-East");
        
        // Create network cost matrix
        int[][] networkCost = new int[][]{{0}};
        
        TaskScheduler scheduler = new TaskScheduler();
        Map<String, String> schedule = scheduler.schedule(
            Arrays.asList(task1),
            Arrays.asList(machine1),
            networkCost
        );
        
        assertThat(schedule).isEmpty();
    }
    
    @Test
    public void testPriorityScheduling() {
        // Create tasks with different priorities
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        resourceReq.put("Memory", 2);
        
        Task task1 = new Task("task1", resourceReq, 100L, 1, new HashSet<>());
        Task task2 = new Task("task2", resourceReq, 100L, 2, new HashSet<>());
        Task task3 = new Task("task3", resourceReq, 100L, 3, new HashSet<>());
        
        // Create machines
        Map<String, Integer> machineRes = new HashMap<>();
        machineRes.put("CPU", 1);
        machineRes.put("Memory", 2);
        
        Machine machine1 = new Machine("machine1", machineRes, "US-East");
        
        // Create network cost matrix
        int[][] networkCost = new int[][]{{0}};
        
        TaskScheduler scheduler = new TaskScheduler();
        Map<String, String> schedule = scheduler.schedule(
            Arrays.asList(task1, task2, task3),
            Arrays.asList(machine1),
            networkCost
        );
        
        // Verify that task3 (highest priority) is scheduled
        assertThat(schedule).containsEntry("task3", "machine1");
    }
    
    @Test
    public void testDependencyHandling() {
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        resourceReq.put("Memory", 2);
        
        Set<String> dependencies = new HashSet<>();
        dependencies.add("task1");
        
        Task task1 = new Task("task1", resourceReq, 100L, 1, new HashSet<>());
        Task task2 = new Task("task2", resourceReq, 100L, 1, dependencies);
        
        Map<String, Integer> machineRes = new HashMap<>();
        machineRes.put("CPU", 2);
        machineRes.put("Memory", 4);
        
        Machine machine1 = new Machine("machine1", machineRes, "US-East");
        
        int[][] networkCost = new int[][]{{0}};
        
        TaskScheduler scheduler = new TaskScheduler();
        Map<String, String> schedule = scheduler.schedule(
            Arrays.asList(task1, task2),
            Arrays.asList(machine1),
            networkCost
        );
        
        assertThat(schedule).containsEntry("task1", "machine1");
    }
    
    @Test
    public void testNetworkCostOptimization() {
        Map<String, Integer> resourceReq = new HashMap<>();
        resourceReq.put("CPU", 1);
        resourceReq.put("Memory", 2);
        
        Task task1 = new Task("task1", resourceReq, 1000L, 1, new HashSet<>());
        
        Map<String, Integer> machineRes = new HashMap<>();
        machineRes.put("CPU", 1);
        machineRes.put("Memory", 2);
        
        Machine machine1 = new Machine("machine1", machineRes, "US-East");
        Machine machine2 = new Machine("machine2", machineRes, "US-West");
        
        // High network cost between machines
        int[][] networkCost = new int[][]{
            {0, 100},
            {100, 0}
        };
        
        TaskScheduler scheduler = new TaskScheduler();
        Map<String, String> schedule = scheduler.schedule(
            Arrays.asList(task1),
            Arrays.asList(machine1, machine2),
            networkCost
        );
        
        // Verify that task is scheduled on machine with lower network cost
        assertThat(schedule).containsEntry("task1", "machine1");
    }
}