import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class NetworkReachTest {
    
    private NetworkReach network;

    @BeforeEach
    public void setUp() {
        network = new NetworkReach();
    }

    @Test
    public void testEmptyNetwork() {
        // No friendships added; no reachability except self-reachability.
        assertFalse(network.is_reachable(1, 2));
        assertTrue(network.is_reachable(1, 1));
    }

    @Test
    public void testDirectReachability() {
        network.add_friendship(1, 2);
        assertTrue(network.is_reachable(1, 2));
        assertFalse(network.is_reachable(2, 1));
    }

    @Test
    public void testIndirectReachability() {
        network.add_friendship(1, 2);
        network.add_friendship(2, 3);
        assertTrue(network.is_reachable(1, 3));
        assertFalse(network.is_reachable(3, 1));
    }

    @Test
    public void testCycleReachability() {
        network.add_friendship(1, 2);
        network.add_friendship(2, 3);
        network.add_friendship(3, 1);
        assertTrue(network.is_reachable(1, 2));
        assertTrue(network.is_reachable(2, 3));
        assertTrue(network.is_reachable(3, 1));
        // In a cycle everyone is reachable from everyone else.
        assertTrue(network.is_reachable(1, 3));
        assertTrue(network.is_reachable(2, 1));
        assertTrue(network.is_reachable(3, 2));
    }

    @Test
    public void testMultiplePaths() {
        // Construct multiple paths: 1->2->4 and 1->3->4, ensuring the algorithm handles simultaneous paths.
        network.add_friendship(1, 2);
        network.add_friendship(2, 4);
        network.add_friendship(1, 3);
        network.add_friendship(3, 4);
        assertTrue(network.is_reachable(1, 4));
        assertFalse(network.is_reachable(4, 1));
    }

    @Test
    public void testNonExistentUser() {
        // Test with friendships involving users not added explicitly before.
        network.add_friendship(10, 20);
        assertTrue(network.is_reachable(10, 20));
        assertFalse(network.is_reachable(20, 10));
    }

    @Test
    public void testSelfReachability() {
        // Every user should be considered reachable to themselves.
        assertTrue(network.is_reachable(1, 1));
        network.add_friendship(1, 2);
        assertTrue(network.is_reachable(1, 1));
        network.add_friendship(2, 3);
        assertTrue(network.is_reachable(2, 2));
    }

    @Test
    public void testLargeNumberOfUsers() {
        // Create a chain of 1000 users: 1 -> 2 -> ... -> 1000.
        int n = 1000;
        for (int i = 1; i < n; i++) {
            network.add_friendship(i, i + 1);
        }
        assertTrue(network.is_reachable(1, 1000));
        assertFalse(network.is_reachable(1000, 1));
    }

    @Test
    public void testDuplicateFriendship() {
        // Duplicate friendship calls should not affect reachability.
        network.add_friendship(1, 2);
        network.add_friendship(1, 2);
        network.add_friendship(1, 2);
        assertTrue(network.is_reachable(1, 2));
    }
}