package optimal_meeting;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class OptimalMeetingTest {

    @Test
    public void testExampleCase() {
        int n = 4;
        int[][] roads = new int[][] {
            {0, 1, 2},
            {0, 2, 5},
            {1, 2, 1},
            {1, 3, 10},
            {2, 3, 1}
        };
        int[] engineerLocations = new int[] {0, 2, 3};
        // Expected optimal meeting point: 2
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(2, result, "Optimal meeting point should be 2");
    }
    
    @Test
    public void testAllEngineersSameLocation() {
        int n = 5;
        int[][] roads = new int[][] {
            {0, 1, 3},
            {1, 2, 4},
            {2, 3, 2},
            {3, 4, 1},
            {0, 4, 10}
        };
        int[] engineerLocations = new int[] {1, 1, 1};
        // When all engineers are at the same location, the best meeting point is that location.
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(1, result, "Meeting point should be the same as the engineers' location.");
    }
    
    @Test
    public void testMultipleOptimalPoints() {
        // In this test, multiple meeting points yield the same total travel time.
        // The function should return the smallest index.
        int n = 3;
        int[][] roads = new int[][] {
            {0, 1, 1},
            {1, 2, 1},
            {0, 2, 2}
        };
        int[] engineerLocations = new int[] {0, 2};
        // Total travel time for meeting at 0: 0 (from 0) + 2 (from 2) = 2
        // for meeting at 1: 1 (from 0) + 1 (from 2) = 2, 
        // for meeting at 2: 2 (from 0) + 0 (from 2) = 2.
        // Expected meeting point is 0 since it is the smallest index.
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(0, result, "Should choose the smallest index when multiple meeting points have equal total travel time.");
    }
    
    @Test
    public void testSparseGraph() {
        int n = 6;
        int[][] roads = new int[][] {
            {0, 1, 5},
            {1, 2, 5},
            {2, 3, 5},
            {3, 4, 5},
            {4, 5, 5}
        };
        int[] engineerLocations = new int[] {0, 5};
        // In a chain graph, all meeting points yield the same total travel time.
        // Total travel time for any meeting point is 25. Therefore, the smallest index (0) should be chosen.
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(0, result, "In a chain graph with equal total travel times, the smallest index should be chosen.");
    }
    
    @Test
    public void testDenseGraph() {
        int n = 5;
        int[][] roads = new int[][] {
            {0, 1, 1},
            {0, 2, 3},
            {0, 3, 4},
            {0, 4, 2},
            {1, 2, 2},
            {1, 3, 6},
            {1, 4, 5},
            {2, 3, 1},
            {2, 4, 7},
            {3, 4, 3}
        };
        int[] engineerLocations = new int[] {1, 2, 3};
        // Compute shortest paths:
        // From computed distances, meeting at 0: total = 1 (from 1) + 3 (from 2) + 4 (from 3) = 8.
        // Meeting at 1: total = 0 (from 1) + 2 (from 2) + 5 (from 3) = 7.
        // Meeting at 2: total = 2 (from 1) + 0 (from 2) + 1 (from 3) = 3.
        // Meeting at 3: total = 5 (from 1) + 1 (from 2) + 0 (from 3) = 6.
        // Meeting at 4: total = 3 (from 1) + 5 (from 2) + 3 (from 3) = 11.
        // Expected meeting point is 2.
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(2, result, "Optimal meeting point should be 2 based on computed shortest paths.");
    }
    
    @Test
    public void testIntegerOverflow() {
        // This test case is designed to check whether the implementation correctly handles very large weight sums.
        int n = 3;
        int[][] roads = new int[][] {
            {0, 1, Integer.MAX_VALUE / 4},
            {1, 2, Integer.MAX_VALUE / 4},
            {0, 2, Integer.MAX_VALUE / 2}
        };
        int[] engineerLocations = new int[] {0, 2};
        // Regardless of the very high travel times, all meeting locations will yield a similar sum.
        // Thus, the function should correctly handle addition without overflow and choose the smallest index: 0.
        int result = OptimalMeeting.findOptimalMeetingPoint(n, roads, engineerLocations);
        assertEquals(0, result, "Should handle large sums without integer overflow and return the smallest index when totals are equal.");
    }
}