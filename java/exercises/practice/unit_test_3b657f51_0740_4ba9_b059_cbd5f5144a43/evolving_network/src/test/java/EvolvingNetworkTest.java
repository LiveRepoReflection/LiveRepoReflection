import org.junit.Before;
import org.junit.Test;
import java.util.List;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class EvolvingNetworkTest {

    private EvolvingNetwork network;

    @Before
    public void setup() {
        network = new EvolvingNetwork();
    }

    @Test
    public void testAddAndRemoveUser() {
        network.addUser(1);
        // Initially, user 1 should have no connections
        List<Integer> connections = network.getConnections(1, 100);
        assertTrue(connections.isEmpty());
        
        // Remove user 1 and expect that calls to getConnections yield empty results.
        network.removeUser(1);
        connections = network.getConnections(1, 200);
        assertTrue(connections.isEmpty());
    }

    @Test
    public void testAddAndUpdateConnection() {
        network.addUser(1);
        network.addUser(2);
        network.addUser(3);

        // Add connection 1->2 at time 10.
        network.addConnection(1, 2, 10);
        List<Integer> connections = network.getConnections(1, 10);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));

        // Adding a new connection between same users at a later time overwrites the earlier one.
        network.addConnection(1, 2, 20);
        // Query at time 15 should still reflect the earlier connection as it's the most recent event <= 15.
        connections = network.getConnections(1, 15);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));
        // Query at time 25 should consider the updated timestamp.
        connections = network.getConnections(1, 25);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));

        // Add another connection 1->3 at time 30.
        network.addConnection(1, 3, 30);
        connections = network.getConnections(1, 35);
        // The result should be sorted in ascending order.
        assertEquals(2, connections.size());
        assertEquals((Integer) 2, connections.get(0));
        assertEquals((Integer) 3, connections.get(1));
    }

    @Test
    public void testRemoveConnection() {
        network.addUser(1);
        network.addUser(2);

        // Add a connection from 1->2 at time 100.
        network.addConnection(1, 2, 100);
        List<Integer> connections = network.getConnections(1, 120);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));

        // Remove the connection at time 150.
        network.removeConnection(1, 2, 150);
        // For query time just before removal timestamp, connection exists.
        connections = network.getConnections(1, 149);
        assertEquals(1, connections.size());
        // At exactly the removal timestamp, the connection should not be considered.
        connections = network.getConnections(1, 150);
        assertTrue(connections.isEmpty());
        // For a later query time, the removal event does not propagate, so the connection is visible.
        connections = network.getConnections(1, 160);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));
    }

    @Test
    public void testCalculateInfluenceScoreSimple() {
        network.addUser(1);
        network.addUser(2);
        network.addUser(3);

        // Create a chain: 1->2 and 2->3 at time 100.
        network.addConnection(1, 2, 100);
        network.addConnection(2, 3, 100);

        // Influence score calculation:
        // Score(3) = 1
        // Score(2) = 1 + decayFactor * Score(3) = 1 + 0.5 * 1 = 1.5
        // Score(1) = 1 + decayFactor * Score(2) = 1 + 0.5 * 1.5 = 1.75
        double decayFactor = 0.5;
        double score = network.calculateInfluenceScore(1, 150, decayFactor);
        assertEquals(1.75, score, 1e-6);
    }

    @Test
    public void testCalculateInfluenceScoreCycle() {
        // Create a cycle: 1->2, 2->3, 3->1.
        network.addUser(1);
        network.addUser(2);
        network.addUser(3);

        network.addConnection(1, 2, 100);
        network.addConnection(2, 3, 100);
        network.addConnection(3, 1, 100);

        // With cycle detection:
        // Let Score(3) = 1 (cycle break when revisiting 1).
        // Then Score(2) = 1 + 0.3 * 1 = 1.3.
        // Then Score(1) = 1 + 0.3 * 1.3 = 1.39.
        double decayFactor = 0.3;
        double score = network.calculateInfluenceScore(1, 150, decayFactor);
        assertEquals(1.39, score, 1e-6);
    }

    @Test
    public void testMultipleConnectionsAtDifferentTimestamps() {
        network.addUser(1);
        network.addUser(2);
        network.addUser(3);
        network.addUser(4);

        // Add multiple connections from user 1 to others at different timestamps.
        network.addConnection(1, 2, 50);
        network.addConnection(1, 3, 100);
        network.addConnection(1, 4, 150);

        // At time 75, only connection to 2 should be visible.
        List<Integer> connections = network.getConnections(1, 75);
        assertEquals(1, connections.size());
        assertEquals((Integer) 2, connections.get(0));

        // At time 125, connections to 2 and 3 should be visible.
        connections = network.getConnections(1, 125);
        assertEquals(2, connections.size());
        assertEquals((Integer) 2, connections.get(0));
        assertEquals((Integer) 3, connections.get(1));

        // At time 200, connections to 2, 3, and 4 should be visible.
        connections = network.getConnections(1, 200);
        assertEquals(3, connections.size());
        assertEquals((Integer) 2, connections.get(0));
        assertEquals((Integer) 3, connections.get(1));
        assertEquals((Integer) 4, connections.get(2));
    }

    @Test
    public void testInfluenceScoreWithNoConnections() {
        network.addUser(10);
        // For a user with no outgoing connections, influence score should be 1.
        double score = network.calculateInfluenceScore(10, 100, 0.5);
        assertEquals(1.0, score, 1e-6);
    }
}