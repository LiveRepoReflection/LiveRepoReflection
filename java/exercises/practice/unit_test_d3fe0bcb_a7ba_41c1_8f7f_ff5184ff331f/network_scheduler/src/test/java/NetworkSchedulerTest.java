package network_scheduler;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import java.util.List;
import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

public class NetworkSchedulerTest {

    private NetworkFlowScheduler scheduler;

    @BeforeEach
    public void setup() {
        scheduler = new NetworkFlowScheduler();
    }

    // Helper class representing a data flow request.
    // This is assumed to mirror the Flow class used by the main solution.
    private static class Flow {
        int source;
        int destination;
        int dataSize;
        int deadline;

        public Flow(int source, int destination, int dataSize, int deadline) {
            this.source = source;
            this.destination = destination;
            this.dataSize = dataSize;
            this.deadline = deadline;
        }
    }

    @Test
    public void testSimpleSchedule() {
        // Basic network: 2 servers, 1 switch.
        int N = 2;
        int M = 1;
        int[][] adjMatrix = {
            {0, 0, 10},
            {0, 0, 5},
            {10, 5, 0}
        };

        List<Flow> flows = new ArrayList<>();
        // Flow from server 0 to server 1, dataSize 10MB, deadline 2s.
        flows.add(new Flow(0, 1, 10, 2));
        // Flow from server 1 to server 0, dataSize 5MB, deadline 1s.
        flows.add(new Flow(1, 0, 5, 1));

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // Expect both flows to be scheduled.
        assertEquals(2, result.size(), "Both flows should be scheduled");
        assertTrue(result.contains(0), "Flow index 0 must be scheduled");
        assertTrue(result.contains(1), "Flow index 1 must be scheduled");
    }

    @Test
    public void testNoValidPath() {
        // Network with no connectivity.
        int N = 2;
        int M = 1;
        int[][] adjMatrix = {
            {0, 0, 0},
            {0, 0, 0},
            {0, 0, 0}
        };

        List<Flow> flows = new ArrayList<>();
        flows.add(new Flow(0, 1, 10, 2));

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // With no valid links, no flow should be scheduled.
        assertEquals(0, result.size(), "No flows can be scheduled when network is disconnected");
    }

    @Test
    public void testBandwidthContention() {
        // Network with shared links that force bandwidth contention.
        // Network consists of 3 servers and 1 switch.
        int N = 3;
        int M = 1;
        int[][] adjMatrix = {
            // Servers 0,1,2 then Switch 0
            {0, 0, 0, 20},
            {0, 0, 0, 20},
            {0, 0, 0, 20},
            {20,20,20, 0}
        };

        List<Flow> flows = new ArrayList<>();
        // Three flows all competing for the same link through the switch.
        flows.add(new Flow(0, 1, 15, 2));
        flows.add(new Flow(1, 2, 15, 2));
        flows.add(new Flow(2, 0, 15, 2));

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // Depending on scheduling and contention, it may not be possible to complete all flows.
        // Our objective is to maximize completed flows within deadline.
        // For this test, verify that at least one flow is scheduled and none of the returned indices is out of range.
        assertFalse(result.isEmpty(), "At least one flow should be scheduled under contention.");
        for (Integer idx : result) {
            assertTrue(idx >= 0 && idx < flows.size(), "Scheduled flow index out of bounds.");
        }
    }

    @Test
    public void testMultiplePathsScenario() {
        // A network with multiple possible paths where choosing the optimal path is critical.
        // Network: 3 servers, 2 switches.
        int N = 3;
        int M = 2;
        int[][] adjMatrix = {
            // Nodes: 0,1,2 (Servers), 3,4 (Switches)
            {0, 0, 0, 15, 0},
            {0, 0, 0, 0, 15},
            {0, 0, 0, 15, 15},
            {15, 0, 15, 0, 10},
            {0, 15, 15, 10, 0}
        };

        List<Flow> flows = new ArrayList<>();
        // Flow with an option to go through switch 3 or 4.
        flows.add(new Flow(0, 1, 20, 3));
        flows.add(new Flow(1, 2, 10, 2));
        flows.add(new Flow(2, 0, 15, 4));

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // Expect that at least the flow with the tightest deadline (flow index 1) gets scheduled,
        // and the scheduler maximizes the number of flows within deadlines.
        assertTrue(result.contains(1), "Flow with index 1 should be scheduled given its easier requirements.");
        for (Integer idx : result) {
            assertTrue(idx >= 0 && idx < flows.size(), "Scheduled flow index out of valid bounds.");
        }
    }

    @Test
    public void testEmptyFlows() {
        // Test when no flows are requested.
        int N = 3;
        int M = 1;
        int[][] adjMatrix = {
            {0, 0, 10, 10},
            {0, 0, 10, 10},
            {10,10, 0, 0},
            {10,10, 0, 0}
        };

        List<Flow> flows = new ArrayList<>();

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // Expect an empty result.
        assertEquals(0, result.size(), "No scheduled flows should be returned when input list is empty.");
    }

    @Test
    public void testAllFlowsMissDeadline() {
        // Create a network where the deadlines are too tight for any flow to complete.
        int N = 2;
        int M = 1;
        int[][] adjMatrix = {
            {0, 0, 5},
            {0, 0, 5},
            {5, 5, 0}
        };

        List<Flow> flows = new ArrayList<>();
        // Each flow requires more time than available due to low bandwidth.
        flows.add(new Flow(0, 1, 100, 1));
        flows.add(new Flow(1, 0, 100, 1));

        List<Integer> result = scheduler.scheduleFlows(N, M, adjMatrix, flows);

        // Expect that no flow completes if the deadlines are impossible.
        assertEquals(0, result.size(), "No flows should be scheduled if deadlines cannot be met.");
    }
}