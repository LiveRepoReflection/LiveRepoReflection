import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MeetingPointTest {

    @Test
    public void testTrivialGraph() {
        int n = 1;
        int[][] edges = {};
        int[] locations = {0};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(0, result);
    }

    @Test
    public void testExampleGraph() {
        int n = 4;
        int[][] edges = { {0, 1, 1}, {0, 2, 5}, {1, 2, 2}, {1, 3, 1} };
        int[] locations = {0, 3};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(1, result);
    }

    @Test
    public void testMultipleOptimalMeetingPoints() {
        // Graph: triangle with a shortcut not available:
        // 0 --10--> 1, 1 --10--> 2, 0 --20--> 2
        // Expected meeting point is node 1.
        int n = 3;
        int[][] edges = { {0, 1, 10}, {1, 2, 10}, {0, 2, 20} };
        int[] locations = {0, 2};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(1, result);
    }

    @Test
    public void testDisconnectedGraph() {
        // Disconnected graph:
        // There is an edge only between 0 and 1. Node 2 is isolated.
        // For any meeting point, at least one individual cannot reach the meeting point.
        // In such cases, distances for unreachable paths are treated as infinite.
        // All nodes result in an infinite maximum distance, so we choose the smallest index (0).
        int n = 3;
        int[][] edges = { {0, 1, 5} };
        int[] locations = {0, 2};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(0, result);
    }

    @Test
    public void testMultipleIndividualsSameLocation() {
        // Multiple individuals starting at the same node.
        // The optimal meeting point should be that starting node.
        int n = 2;
        int[][] edges = { {0, 1, 3} };
        int[] locations = {0, 0};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(0, result);
    }

    @Test
    public void testTieBreakerSmallestIndex() {
        // Graph with a clear tie situation:
        // n = 3, 0--4-->1, 1--4-->2 (undirected).
        // Locations are at nodes 0 and 2.
        // For node 0: max(distance(0,0)=0, distance(2,0)=8) = 8.
        // For node 1: max(distance(0,1)=4, distance(2,1)=4) = 4.
        // For node 2: max(distance(0,2)=8, distance(2,2)=0) = 8.
        // Only node 1 gives minimum maximum distance.
        int n = 3;
        int[][] edges = { {0, 1, 4}, {1, 2, 4} };
        int[] locations = {0, 2};
        int result = MeetingPoint.findMeetingPoint(n, edges, locations);
        assertEquals(1, result);
    }
}