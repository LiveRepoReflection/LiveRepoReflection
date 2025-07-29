package network_sim;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Comprehensive unit tests for the NetworkSimulation.
 * Assumes existence of the following methods in NetworkSimulation:
 * - void addServer(String id, int processingCapacity, int processingSpeed, int securityLevel)
 * - void addConnection(String sourceServerId, String targetServerId, int latency)
 * - void addTask(String id, int size, int securityRequirement, int priority, String sourceServerId, String destinationServerId)
 * - void processTasks()  // Processes tasks synchronously in the simulation for testing purposes.
 * - String getTaskStatus(String taskId) // Returns "COMPLETED", "FAILED", or "IN_PROGRESS"
 * - List<String> getOverloadedServers() // Returns list of server IDs that are overloaded.
 * - List<String> getSecurityBreaches()   // Returns list of task IDs or breach descriptions for tasks that violated security requirements.
 * - double getAverageLatency()           // Returns the average latency for task completion.
 * - int getFailedTaskCount()             // Returns the total number of tasks that failed due to unreachable destination.
 * - void failServer(String serverId)     // Simulates a server failure event.
 * - void recoverServer(String serverId)  // Simulates a server recovery event.
 * - void failConnection(String sourceServerId, String targetServerId)  // Simulates a connection failure event.
 * - void recoverConnection(String sourceServerId, String targetServerId, int latency) // Simulates connection recovery event.
 *
 * This test class covers:
 * - Basic task routing and processing.
 * - Overloaded server detection.
 * - Security breach detection.
 * - Dynamic events for server and connection failures and recoveries.
 * - Average latency calculation.
 */
public class NetworkSimTest {

    private NetworkSimulation simulation;

    @BeforeEach
    public void setUp() {
        simulation = new NetworkSimulation();
    }

    @Test
    public void testSimpleTaskRoutingAndCompletion() {
        // Set up servers with sufficient capacity and security.
        simulation.addServer("server1", 10, 5, 5);
        simulation.addServer("server2", 10, 5, 5);
        // Set up a connection from server1 to server2 with low latency.
        simulation.addConnection("server1", "server2", 10);
        // Add a high priority task from server1 to server2.
        simulation.addTask("task1", 20, 4, 10, "server1", "server2");

        // Process tasks.
        simulation.processTasks();

        // Verify that task1 is completed.
        String status = simulation.getTaskStatus("task1");
        assertEquals("COMPLETED", status, "Task should be completed successfully.");
    }

    @Test
    public void testOverloadedServerDetection() {
        // Set up a single server with limited capacity.
        simulation.addServer("server_overload", 2, 5, 5);
        // No connection needed as tasks originate and complete on the same server.
        // Add three tasks to overload the server.
        simulation.addTask("task1", 10, 3, 5, "server_overload", "server_overload");
        simulation.addTask("task2", 10, 3, 4, "server_overload", "server_overload");
        simulation.addTask("task3", 10, 3, 3, "server_overload", "server_overload");

        // Process tasks.
        simulation.processTasks();

        // The server should be flagged as overloaded.
        List<String> overloadedServers = simulation.getOverloadedServers();
        assertTrue(overloadedServers.contains("server_overload"), "Server should be detected as overloaded.");
    }

    @Test
    public void testSecurityBreachDetection() {
        // Set up servers with varying security levels.
        simulation.addServer("low_security_server", 10, 5, 3);
        simulation.addServer("destination_server", 10, 5, 5);
        simulation.addConnection("low_security_server", "destination_server", 15);
        // Add a task that requires a higher security level than low_security_server provides.
        simulation.addTask("insecure_task", 15, 5, 8, "low_security_server", "destination_server");

        // Process tasks.
        simulation.processTasks();

        // The simulation should detect a security breach.
        List<String> breaches = simulation.getSecurityBreaches();
        assertTrue(breaches.contains("insecure_task"), "Security breach should be detected for the task.");
    }

    @Test
    public void testServerFailureAndRecovery() {
        // Set up three servers in a line: serverA -> serverB -> serverC.
        simulation.addServer("serverA", 10, 5, 5);
        simulation.addServer("serverB", 10, 5, 5);
        simulation.addServer("serverC", 10, 5, 5);
        simulation.addConnection("serverA", "serverB", 10);
        simulation.addConnection("serverB", "serverC", 10);

        // Add a task from serverA to serverC.
        simulation.addTask("task_fail_recov", 25, 4, 7, "serverA", "serverC");

        // Process tasks initially.
        simulation.processTasks();
        // At this point, task should be in progress or completed.
        String initialStatus = simulation.getTaskStatus("task_fail_recov");
        // Now simulate failure of intermediate server serverB.
        simulation.failServer("serverB");
        // Process tasks again to force rerouting.
        simulation.processTasks();

        // Verify that task is either rerouted successfully or marked as failed.
        String statusAfterFailure = simulation.getTaskStatus("task_fail_recov");
        // If the task is marked failed due to unreachable destination, it should be tracked.
        int failedCountAfterFailure = simulation.getFailedTaskCount();
        // Recover serverB.
        simulation.recoverServer("serverB");
        simulation.processTasks();
        // After recovery, task should complete if not already failed.
        String finalStatus = simulation.getTaskStatus("task_fail_recov");
        if (failedCountAfterFailure == 0) {
            assertEquals("COMPLETED", finalStatus, "Task should be completed after server recovery.");
        } else {
            assertEquals("FAILED", finalStatus, "Task failed due to server unavailability before recovery.");
        }
    }

    @Test
    public void testConnectionFailureAndRecovery() {
        // Set up servers with connection: serverX -> serverY.
        simulation.addServer("serverX", 10, 5, 5);
        simulation.addServer("serverY", 10, 5, 5);
        simulation.addConnection("serverX", "serverY", 10);

        // Add a task from serverX to serverY.
        simulation.addTask("task_conn", 20, 4, 9, "serverX", "serverY");

        // Process tasks normally.
        simulation.processTasks();
        String statusBeforeFailure = simulation.getTaskStatus("task_conn");
        assertEquals("COMPLETED", statusBeforeFailure, "Task should be completed normally.");

        // Reset simulation state with a new task for connection failure testing.
        simulation = new NetworkSimulation();
        simulation.addServer("serverX", 10, 5, 5);
        simulation.addServer("serverY", 10, 5, 5);
        simulation.addConnection("serverX", "serverY", 10);
        simulation.addTask("task_conn_failure", 20, 4, 9, "serverX", "serverY");

        // Simulate connection failure.
        simulation.failConnection("serverX", "serverY");
        simulation.processTasks();
        String statusDuringFailure = simulation.getTaskStatus("task_conn_failure");
        // Expect task to eventually be marked as failed since the destination is unreachable.
        assertEquals("FAILED", statusDuringFailure, "Task should be marked as failed due to connection failure.");

        // Recover connection.
        simulation.recoverConnection("serverX", "serverY", 10);
        // Add another task after recovery.
        simulation.addTask("task_conn_recovery", 20, 4, 9, "serverX", "serverY");
        simulation.processTasks();
        String statusAfterRecovery = simulation.getTaskStatus("task_conn_recovery");
        assertEquals("COMPLETED", statusAfterRecovery, "Task should be completed after connection recovery.");
    }

    @Test
    public void testAverageLatencyCalculation() {
        // Set up servers and connections.
        simulation.addServer("server1", 10, 5, 5);
        simulation.addServer("server2", 10, 5, 5);
        simulation.addServer("server3", 10, 5, 5);
        simulation.addConnection("server1", "server2", 10);
        simulation.addConnection("server2", "server3", 20);

        // Add tasks with varying latencies.
        simulation.addTask("task_latency1", 15, 4, 8, "server1", "server3");
        simulation.addTask("task_latency2", 25, 4, 7, "server1", "server3");
        simulation.addTask("task_latency3", 35, 4, 9, "server1", "server3");

        simulation.processTasks();

        double avgLatency = simulation.getAverageLatency();
        // Since connections have latencies, avgLatency should be at least the sum of path latencies.
        assertTrue(avgLatency >= 30, "Average latency should be no less than the minimal path latency (10 + 20).");
    }
}