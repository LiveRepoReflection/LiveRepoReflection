import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TaskSchedulerTest {

    @Test
    public void testExampleCase() {
        int[] deadlines = {2, 4, 2, 1};
        int[] times = {3, 2, 1, 4};
        int[] penalties = {4, 5, 2, 7};
        long expected = 11;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }

    @Test
    public void testNoPenaltyCase() {
        int[] deadlines = {5, 5};
        int[] times = {3, 1};
        int[] penalties = {6, 3};
        long expected = 0;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }

    @Test
    public void testAllMissedCase() {
        int[] deadlines = {1, 1};
        int[] times = {5, 3};
        int[] penalties = {10, 15};
        long expected = 25;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }

    @Test
    public void testSingleTaskExactDeadline() {
        int[] deadlines = {3};
        int[] times = {3};
        int[] penalties = {8};
        long expected = 0;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }

    @Test
    public void testLargeNumbersCase() {
        int[] deadlines = {1000000000, 1000000000};
        int[] times = {500000000, 600000000};
        int[] penalties = {1000000000, 2000000000};
        long expected = 1000000000L;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }

    @Test
    public void testPreemptionBenefitCase() {
        // In this case, preemption is necessary to minimize penalty.
        // Task A: deadline = 4, time = 5, penalty = 10
        // Task B: deadline = 3, time = 2, penalty = 5
        // Task C: deadline = 6, time = 1, penalty = 7
        // Optimally, completing task B and C on time forces task A to miss its deadline incurring a penalty of 10.
        int[] deadlines = {4, 3, 6};
        int[] times = {5, 2, 1};
        int[] penalties = {10, 5, 7};
        long expected = 10;
        long actual = TaskScheduler.minTotalPenalty(deadlines, times, penalties);
        assertEquals(expected, actual);
    }
}