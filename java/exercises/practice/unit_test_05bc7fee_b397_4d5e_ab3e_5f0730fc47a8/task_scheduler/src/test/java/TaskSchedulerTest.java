import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

public class TaskSchedulerTest {

    @Test
    public void testSingleTaskSingleWorker() {
        int N = 1;
        List<Task> tasks = Arrays.asList(new Task(10, 20));
        // Only one task: finish time = 10, lateness = 10 - 20 = -10.
        int expected = -10;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Single task on one worker should yield a maximum lateness of -10.");
    }

    @Test
    public void testMultipleTasksSingleWorker() {
        int N = 1;
        List<Task> tasks = Arrays.asList(
            new Task(4, 5),
            new Task(3, 7),
            new Task(2, 6)
        );
        // Best ordering by deadline (EDD): (4,5), (2,6), (3,7):
        // Completion times: 4 -> lateness: -1, 6 -> 0, 9 -> 2.
        // Maximum lateness = 2.
        int expected = 2;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Single worker with three tasks should yield maximum lateness of 2.");
    }

    @Test
    public void testMultipleWorkersOptimizedSchedule() {
        int N = 2;
        List<Task> tasks = Arrays.asList(
            new Task(50, 100),
            new Task(30, 150),
            new Task(20, 60),
            new Task(40, 80)
        );
        // One possible optimal schedule from the prompt example gives a maximum lateness of -30.
        int expected = -30;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Example schedule with two workers should yield maximum lateness of -30.");
    }

    @Test
    public void testParallelExecutionWhenWorkersExceedTasks() {
        // When workers are more than or equal to tasks, each task runs concurrently.
        int N = 4;
        List<Task> tasks = Arrays.asList(
            new Task(1, 5),   // finish time = 1, lateness = -4
            new Task(2, 6),   // finish time = 2, lateness = -4
            new Task(3, 7),   // finish time = 3, lateness = -4
            new Task(4, 20)   // finish time = 4, lateness = -16
        );
        // Maximum lateness = max(-4, -4, -4, -16) = -4.
        int expected = -4;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Each task can run concurrently; maximum lateness should be -4.");
    }

    @Test
    public void testTightDeadlinesForceLateness() {
        int N = 2;
        List<Task> tasks = Arrays.asList(
            new Task(10, 5),
            new Task(10, 5)
        );
        // Even if scheduled concurrently, each finishes at 10 leading to lateness 5.
        int expected = 5;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Tasks with tight deadlines should yield a maximum lateness of 5.");
    }

    @Test
    public void testMixedTaskSet() {
        int N = 2;
        List<Task> tasks = Arrays.asList(
            new Task(3, 4),  // deadline 4
            new Task(2, 3),  // deadline 3
            new Task(4, 9),  // deadline 9
            new Task(1, 2)   // deadline 2
        );
        // One possible optimal assignment:
        // Sort tasks by deadline: (1,2), (2,3), (3,4), (4,9)
        // Assign (1,2) -> Worker1: finish=1, lateness=-1.
        // Assign (2,3) -> Worker2: finish=2, lateness=-1.
        // Assign (3,4) -> Worker1 (earliest finish): finish=1+3=4, lateness=0.
        // Assign (4,9) -> Worker2: finish=2+4=6, lateness=-3.
        // Maximum lateness = max(-1,-1,0,-3) = 0.
        int expected = 0;
        int result = TaskScheduler.minimizeMaxLateness(N, tasks);
        assertEquals(expected, result, "Mixed tasks with two workers should yield a maximum lateness of 0.");
    }
}