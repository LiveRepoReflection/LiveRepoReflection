import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class OptimalMeetingTest {

    @Test
    public void testLineGraphEmployeesAtEnds() {
        int n = 3;
        int[][] edges = new int[][] {
            {0, 1, 1},
            {1, 2, 1}
        };
        int[] employeeLocations = new int[] {0, 2};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(1, result, "Expected meeting point at node 1");
    }

    @Test
    public void testSingleEmployee() {
        int n = 5;
        int[][] edges = new int[][] {
            {0, 1, 2},
            {1, 2, 2},
            {2, 3, 2},
            {3, 4, 2}
        };
        int[] employeeLocations = new int[] {3};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(3, result, "Expected meeting point to be the employee's location");
    }

    @Test
    public void testStarGraph() {
        int n = 5;
        int[][] edges = new int[][] {
            {0, 1, 1},
            {0, 2, 1},
            {0, 3, 1},
            {0, 4, 1}
        };
        int[] employeeLocations = new int[] {1, 2, 3, 4};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(0, result, "Expected meeting point at the center node 0");
    }

    @Test
    public void testTieBreakSmallIndex() {
        int n = 4;
        int[][] edges = new int[][] {
            {0, 1, 1},
            {1, 2, 1},
            {2, 3, 1}
        };
        int[] employeeLocations = new int[] {0, 3};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(1, result, "Expected meeting point at node 1 due to tie-break on smallest index");
    }

    @Test
    public void testDenseGraph() {
        int n = 6;
        int[][] edges = new int[][] {
            {0, 1, 4},
            {0, 2, 2},
            {1, 2, 1},
            {1, 3, 5},
            {2, 3, 8},
            {2, 4, 10},
            {3, 4, 2},
            {3, 5, 6},
            {4, 5, 3}
        };
        int[] employeeLocations = new int[] {0, 4, 5};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(3, result, "Expected meeting point at node 3 for the dense graph");
    }

    @Test
    public void testTreeGraph() {
        int n = 7;
        int[][] edges = new int[][] {
            {0, 1, 3},
            {0, 2, 2},
            {1, 3, 4},
            {1, 4, 1},
            {2, 5, 6},
            {2, 6, 5}
        };
        int[] employeeLocations = new int[] {3, 4, 5, 6};
        OptimalMeeting solver = new OptimalMeeting();
        int result = solver.findOptimalMeetingPoint(n, edges, employeeLocations);
        assertEquals(0, result, "Expected meeting point at node 0 for the tree graph");
    }
}