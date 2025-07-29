import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;
import java.util.*;

class TaskSchedulerTest {

    @Test
    void testSimpleSchedule() {
        // Create worker nodes
        List<Node> nodes = List.of(
            new Node(4, 16, 1),  // 4 CPU cores, 16GB RAM, 1 GPU
            new Node(8, 32, 2)   // 8 CPU cores, 32GB RAM, 2 GPUs
        );

        // Create tasks
        List<Task> tasks = List.of(
            new Task(2, 8, 1, 60),   // Task1: 2 cores, 8GB, 1 GPU, 60s
            new Task(4, 16, 0, 30)    // Task2: 4 cores, 16GB, 0 GPU, 30s
        );

        // No dependencies
        List<Pair<Task, Task>> dependencies = new ArrayList<>();

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        Map<Task, Assignment> schedule = scheduler.schedule();

        assertThat(schedule).hasSize(2);
        assertThat(schedule.get(tasks.get(0)).getStartTimeSeconds()).isGreaterThanOrEqualTo(0);
        assertThat(schedule.get(tasks.get(1)).getStartTimeSeconds()).isGreaterThanOrEqualTo(0);
    }

    @Test
    void testScheduleWithDependencies() {
        List<Node> nodes = List.of(
            new Node(4, 16, 1)
        );

        List<Task> tasks = List.of(
            new Task(2, 8, 0, 60),    // Task1
            new Task(2, 8, 0, 30)     // Task2 (depends on Task1)
        );

        List<Pair<Task, Task>> dependencies = List.of(
            new Pair<>(tasks.get(0), tasks.get(1))  // Task2 depends on Task1
        );

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        Map<Task, Assignment> schedule = scheduler.schedule();

        assertThat(schedule).hasSize(2);
        int task1Start = schedule.get(tasks.get(0)).getStartTimeSeconds();
        int task2Start = schedule.get(tasks.get(1)).getStartTimeSeconds();
        
        assertThat(task2Start).isGreaterThanOrEqualTo(task1Start + tasks.get(0).getExecutionTimeSeconds());
    }

    @Test
    void testInsufficientResources() {
        List<Node> nodes = List.of(
            new Node(2, 8, 0)  // Node with limited resources
        );

        List<Task> tasks = List.of(
            new Task(4, 16, 0, 60)  // Task requiring more resources than available
        );

        List<Pair<Task, Task>> dependencies = new ArrayList<>();

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        
        assertThatThrownBy(() -> scheduler.schedule())
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("No feasible schedule found");
    }

    @Test
    void testComplexScheduleWithMultipleNodesAndTasks() {
        List<Node> nodes = List.of(
            new Node(8, 32, 2),
            new Node(4, 16, 1),
            new Node(16, 64, 4)
        );

        List<Task> tasks = List.of(
            new Task(4, 16, 1, 120),  // Task1
            new Task(8, 32, 2, 180),  // Task2
            new Task(2, 8, 0, 60),    // Task3
            new Task(6, 24, 1, 90)    // Task4
        );

        List<Pair<Task, Task>> dependencies = List.of(
            new Pair<>(tasks.get(0), tasks.get(1)),
            new Pair<>(tasks.get(2), tasks.get(3))
        );

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        Map<Task, Assignment> schedule = scheduler.schedule();

        assertThat(schedule).hasSize(4);
        
        // Verify dependencies are respected
        int task1Start = schedule.get(tasks.get(0)).getStartTimeSeconds();
        int task2Start = schedule.get(tasks.get(1)).getStartTimeSeconds();
        int task3Start = schedule.get(tasks.get(2)).getStartTimeSeconds();
        int task4Start = schedule.get(tasks.get(3)).getStartTimeSeconds();

        assertThat(task2Start).isGreaterThanOrEqualTo(task1Start + tasks.get(0).getExecutionTimeSeconds());
        assertThat(task4Start).isGreaterThanOrEqualTo(task3Start + tasks.get(2).getExecutionTimeSeconds());
    }

    @Test
    void testCyclicDependencies() {
        List<Node> nodes = List.of(new Node(4, 16, 1));
        List<Task> tasks = List.of(
            new Task(2, 8, 0, 60),
            new Task(2, 8, 0, 60)
        );

        List<Pair<Task, Task>> dependencies = List.of(
            new Pair<>(tasks.get(0), tasks.get(1)),
            new Pair<>(tasks.get(1), tasks.get(0))  // Creates a cycle
        );

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        
        assertThatThrownBy(() -> scheduler.schedule())
            .isInstanceOf(IllegalStateException.class)
            .hasMessageContaining("Cyclic dependencies detected");
    }

    @Test
    void testLargeScaleScheduling() {
        // Create 50 nodes with varying resources
        List<Node> nodes = new ArrayList<>();
        for (int i = 0; i < 50; i++) {
            nodes.add(new Node(4 + (i % 12), 16 + (i % 48), i % 4));
        }

        // Create 500 tasks with varying requirements
        List<Task> tasks = new ArrayList<>();
        for (int i = 0; i < 500; i++) {
            tasks.add(new Task(1 + (i % 4), 4 + (i % 16), i % 2, 30 + (i % 120)));
        }

        // Create some dependencies (each task depends on previous task)
        List<Pair<Task, Task>> dependencies = new ArrayList<>();
        for (int i = 0; i < tasks.size() - 1; i += 2) {
            dependencies.add(new Pair<>(tasks.get(i), tasks.get(i + 1)));
        }

        TaskScheduler scheduler = new TaskScheduler(nodes, tasks, dependencies);
        Map<Task, Assignment> schedule = scheduler.schedule();

        assertThat(schedule).hasSize(tasks.size());
        
        // Verify all dependencies are respected
        for (Pair<Task, Task> dep : dependencies) {
            int startTime1 = schedule.get(dep.getFirst()).getStartTimeSeconds();
            int endTime1 = startTime1 + dep.getFirst().getExecutionTimeSeconds();
            int startTime2 = schedule.get(dep.getSecond()).getStartTimeSeconds();
            
            assertThat(startTime2).isGreaterThanOrEqualTo(endTime1);
        }
    }
}