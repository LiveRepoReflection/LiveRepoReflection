package meeting_point;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class MeetingPointTest {

    @Test
    public void testSingleLocation() {
        int n = 1;
        int[][] roads = {};
        int[] friends = {0};
        // Only one location, so the maximum travel time is 0.
        int result = MeetingPoint.findOptimalMeetingPoint(n, roads, friends);
        assertEquals(0, result);
    }
    
    @Test
    public void testSimpleEdge() {
        int n = 2;
        int[][] roads = {
            {0, 1, 5}
        };
        int[] friends = {0, 1};
        // Meeting at either node results in a travel time of 5 for one friend.
        int result = MeetingPoint.findOptimalMeetingPoint(n, roads, friends);
        assertEquals(5, result);
    }
    
    @Test
    public void testTriangleGraph() {
        int n = 3;
        int[][] roads = {
            {0, 1, 3},
            {1, 2, 3},
            {0, 2, 10}
        };
        int[] friends = {0, 2};
        // Optimal meeting point is at node 1 with both friends traveling 3.
        int result = MeetingPoint.findOptimalMeetingPoint(n, roads, friends);
        assertEquals(3, result);
    }
    
    @Test
    public void testDisconnectedGraph() {
        int n = 4;
        int[][] roads = {
            {0, 1, 4},
            {2, 3, 5}
        };
        int[] friends = {0, 2};
        // Friends are in separate disconnected components, hence no meeting point is possible.
        int result = MeetingPoint.findOptimalMeetingPoint(n, roads, friends);
        assertEquals(-1, result);
    }
    
    @Test
    public void testComplexGraph() {
        int n = 6;
        int[][] roads = {
            {0, 1, 1},
            {1, 4, 2},
            {0, 3, 4},
            {3, 4, 3},
            {4, 5, 1}
        };
        int[] friends = {0, 5};
        // There are multiple candidate meeting points.
        // For example, meeting at node 1: friend0 travels distance 1, friend5 travels 5->4->1: 1+2 = 3.
        // Meeting at node 4: friend0 travels 0->1->4: 1+2 = 3, friend5 travels 1.
        // Hence, the minimum possible maximum travel time is 3.
        int result = MeetingPoint.findOptimalMeetingPoint(n, roads, friends);
        assertEquals(3, result);
    }
}