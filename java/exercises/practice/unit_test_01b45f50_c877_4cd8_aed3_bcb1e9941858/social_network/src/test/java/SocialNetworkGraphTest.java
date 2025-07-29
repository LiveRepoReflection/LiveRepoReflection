import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class SocialNetworkGraphTest {

    private SocialNetworkGraph graph;

    @BeforeEach
    public void setup() {
        graph = new SocialNetworkGraph();
    }

    @Test
    public void testAddUserAndGetFriendsEmpty() {
        // Initially, the user does not exist so getFriends should return an empty list.
        assertEquals(Collections.emptyList(), graph.getFriends(1));

        graph.addUser(1);
        // Added user should have no friends.
        assertEquals(Collections.emptyList(), graph.getFriends(1));

        // Add the same user again should not affect the state.
        graph.addUser(1);
        assertEquals(Collections.emptyList(), graph.getFriends(1));
    }

    @Test
    public void testAddConnectionAndGetFriends() {
        // Adding connection should auto-add users if they do not exist.
        graph.addConnection(1, 2);
        List<Long> friendsOf1 = graph.getFriends(1);
        List<Long> friendsOf2 = graph.getFriends(2);
        // Both users should have one friend each.
        assertEquals(Arrays.asList(2L), friendsOf1);
        assertEquals(Arrays.asList(1L), friendsOf2);

        // Add more connections.
        graph.addConnection(1, 3);
        graph.addConnection(1, 4);
        // getFriends should return sorted list.
        friendsOf1 = graph.getFriends(1);
        assertEquals(Arrays.asList(2L, 3L, 4L), friendsOf1);

        // Attempting to add duplicate connection should be ignored.
        graph.addConnection(1, 2);
        friendsOf1 = graph.getFriends(1);
        assertEquals(Arrays.asList(2L, 3L, 4L), friendsOf1);
    }

    @Test
    public void testRemoveConnection() {
        graph.addConnection(1, 2);
        graph.addConnection(1, 3);
        // Verify initial setup
        assertEquals(Arrays.asList(2L, 3L), graph.getFriends(1));

        // Remove connection that exists.
        graph.removeConnection(1, 2);
        assertEquals(Arrays.asList(3L), graph.getFriends(1));
        assertEquals(Collections.emptyList(), graph.getFriends(2));

        // Removing a non-existing connection should not throw.
        graph.removeConnection(1, 4);
        assertEquals(Arrays.asList(3L), graph.getFriends(1));
    }

    @Test
    public void testGetMutualFriends() {
        // Setup a triangle: 1-2, 1-3, 2-3
        graph.addConnection(1, 2);
        graph.addConnection(1, 3);
        graph.addConnection(2, 3);

        List<Long> mutual12 = graph.getMutualFriends(1, 2);
        // Both 1 and 2 are connected to 3.
        assertEquals(Arrays.asList(3L), mutual12);

        // Mutual friends for non-connected users with no overlap
        graph.addUser(4);
        List<Long> mutual14 = graph.getMutualFriends(1, 4);
        assertEquals(Collections.emptyList(), mutual14);
    }

    @Test
    public void testGetRecommendedFriends() {
        // Create the following network:
        // 1 is connected to 2, 3.
        // 2 is connected to 1, 3, 4.
        // 3 is connected to 1, 2, 4, 5.
        // 4 is connected to 2, 3.
        // 5 is connected to 3.
        graph.addConnection(1, 2);
        graph.addConnection(1, 3);
        graph.addConnection(2, 3);
        graph.addConnection(2, 4);
        graph.addConnection(3, 4);
        graph.addConnection(3, 5);

        // For user 1: potential recommendations: 4 and 5.
        // Mutual friends count:
        // 4: mutual friends with 1 are 2 and 3 (count 2)
        // 5: mutual friend with 1 is 3 (count 1)
        List<Long> rec1 = graph.getRecommendedFriends(1, 5);
        // Should be sorted in descending order by mutual friend count,
        // and tie resolved in ascending user id (if needed).
        assertEquals(Arrays.asList(4L, 5L), rec1);

        // For user 4: potential recommendations: 1 and 5.
        // 1: mutual friends 2 and 3 (count 2)
        // 5: mutual friend 3 (count 1)
        List<Long> rec4 = graph.getRecommendedFriends(4, 2);
        assertEquals(Arrays.asList(1L, 5L), rec4);

        // Test limit recommendationCount.
        List<Long> rec3 = graph.getRecommendedFriends(3, 1);
        // For user 3, friends are 1, 2, 4, 5 so no recommendation possible.
        assertEquals(Collections.emptyList(), rec3);
    }

    @Test
    public void testEdgeCasesNonExistingUser() {
        // Non-existing user for getFriends.
        assertEquals(Collections.emptyList(), graph.getFriends(100));

        // Non-existing users for mutual friends.
        assertEquals(Collections.emptyList(), graph.getMutualFriends(100, 200));

        // Non-existing user for recommendations.
        assertEquals(Collections.emptyList(), graph.getRecommendedFriends(300, 3));
    }

    @Test
    public void testNoSelfConnection() {
        // Attempt to add a connection from a user to themselves.
        graph.addConnection(1, 1);
        // There should be no self-connection.
        assertEquals(Collections.emptyList(), graph.getFriends(1));
    }

    @Test
    public void testComplexRecommendationOrdering() {
        // Create a more complex scenario where tie-breaking is necessary.
        // Setup:
        // 1 is connected to 2, 3.
        // 2 is connected to 1, 4, 5.
        // 3 is connected to 1, 4, 6.
        // 4,5,6 are not directly connected to 1.
        // Mutual counts for potential recommendation for 1:
        // 4: from 2 and 3 (count 2)
        // 5: from 2 (count 1)
        // 6: from 3 (count 1)
        graph.addConnection(1, 2);
        graph.addConnection(1, 3);
        graph.addConnection(2, 4);
        graph.addConnection(2, 5);
        graph.addConnection(3, 4);
        graph.addConnection(3, 6);

        List<Long> rec1 = graph.getRecommendedFriends(1, 3);
        // Expected: 4 (count 2), then 5 and 6 (both count 1) but 5 comes before 6 due to lower ID.
        assertEquals(Arrays.asList(4L, 5L, 6L), rec1);
    }
}