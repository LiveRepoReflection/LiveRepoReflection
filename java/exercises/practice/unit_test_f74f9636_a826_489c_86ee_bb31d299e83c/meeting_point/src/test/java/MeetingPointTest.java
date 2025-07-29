import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

import static org.junit.jupiter.api.Assertions.*;

public class MeetingPointTest {

    // Assuming the implementation class is MeetingPoint with method:
    // public int findOptimalMeetingPoint(int n, int[][] edges, int[] employeeLocations, int maxTravelTime)
    private final MeetingPoint meetingPoint = new MeetingPoint();

    @Test
    public void testOptimalMeetingSimple() {
        int n = 4;
        int[][] edges = {
            {0, 1, 1},
            {0, 2, 5},
            {1, 2, 2},
            {1, 3, 1}
        };
        int[] employeeLocations = {0, 1, 2, 3};
        int maxTravelTime = 10;

        int expected = 1;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "Optimal meeting point should be building 1");
    }

    @Test
    public void testEmptyGraph() {
        // n = 0; no buildings available.
        int n = 0;
        int[][] edges = {};
        int[] employeeLocations = {};
        int maxTravelTime = 0;

        int expected = -1;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "Empty graph should return -1 (no valid meeting location)");
    }

    @Test
    public void testGraphWithNoEdgesAndMultipleBuildings() {
        // n > 0 but no roads connecting them.
        int n = 3;
        int[][] edges = {}; // no connections
        // If employees are in different isolated buildings, then no meeting point can be reached by all.
        int[] employeeLocations = {0, 1};
        int maxTravelTime = 100;

        int expected = -1;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "With no connecting roads, no valid meeting point exists (except if employees are co-located)");
    }

    @Test
    public void testDisconnectedGraph() {
        // Create a graph with two disconnected components.
        int n = 5;
        int[][] edges = {
            {0, 1, 3},
            {1, 2, 4},
            // Buildings 3 and 4 are connected only to each other.
            {3, 4, 2}
        };
        // One employee is in the component {0,1,2} and one in the component {3,4}
        int[] employeeLocations = {0, 3};
        int maxTravelTime = 20;

        int expected = -1;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "Employees in disconnected components result in no valid meeting point");
    }

    @Test
    public void testTieBreakingMeetingPoint() {
        // Create a scenario where two buildings yield the same total commute time.
        int n = 4;
        int[][] edges = {
            {0, 1, 2},
            {1, 2, 2},
            {2, 3, 2},
            {0, 3, 6}
        };
        // Two employees located at buildings 0 and 3.
        int[] employeeLocations = {0, 3};
        int maxTravelTime = 10;
        // Total commute time from:
        // Building 0: 0 (from 0) + 6 (from 3 via 2,1? or direct 3->0 = 6) = 6
        // Building 1: 2 (from 0) + 4 (from 3: 3->2->1) = 6
        // Building 2: 4 (from 0: 0->1->2) + 2 (from 3) = 6
        // Building 3: 6 (from 0) + 0 = 6
        // All are equal; expect the smallest building number, i.e., 0.
        int expected = 0;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "Tie-breaking should return the smallest building number");
    }

    @Test
    public void testMaxTravelTimeExceeded() {
        // Valid connected graph but optimal total commute time exceeds maxTravelTime constraint.
        int n = 3;
        int[][] edges = {
            {0, 1, 50},
            {1, 2, 50}
        };
        int[] employeeLocations = {0, 2};
        int maxTravelTime = 90; // Optimal total is 100 (from building 1: 50+50)
        int expected = -1;
        int actual = meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertEquals(expected, actual, "When minimum total commute time exceeds maxTravelTime, expect -1");
    }

    @Test
    public void testInvalidEmployeeLocation() {
        // Employee location is outside the valid range.
        int n = 3;
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5}
        };
        int[] employeeLocations = {0, 3}; // 3 is an invalid building number for n = 3
        int maxTravelTime = 20;
        
        Executable executable = () -> meetingPoint.findOptimalMeetingPoint(n, edges, employeeLocations, maxTravelTime);
        assertThrows(IllegalArgumentException.class, executable, "Invalid employee location should throw IllegalArgumentException");
    }
}