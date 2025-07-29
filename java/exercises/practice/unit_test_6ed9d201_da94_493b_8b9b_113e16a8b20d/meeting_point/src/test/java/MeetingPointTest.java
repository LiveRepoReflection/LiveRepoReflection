import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.List;

public class MeetingPointTest {
    private static final double DELTA = 0.001;

    @Test
    public void testSingleUser() {
        User user = new User(40.7128, -74.0060, 1);
        List<User> users = Arrays.asList(user);
        double radius = 10.0;
        
        OptimalMeetingPoint result = MeetingPoint.findOptimalMeetingPoint(users, radius);
        
        assertEquals(40.7128, result.getLatitude(), DELTA);
        assertEquals(-74.0060, result.getLongitude(), DELTA);
        assertEquals(0.0, result.getTotalCommunicationCost(), DELTA);
    }

    @Test
    public void testTwoUsersWithinRadius() {
        User user1 = new User(40.7128, -74.0060, 1);
        User user2 = new User(40.7138, -74.0050, 2);
        List<User> users = Arrays.asList(user1, user2);
        double radius = 1.5;
        
        OptimalMeetingPoint result = MeetingPoint.findOptimalMeetingPoint(users, radius);
        
        assertTrue(result.getTotalCommunicationCost() > 0);
        assertTrue(result.getTotalCommunicationCost() < 1.5);
    }

    @Test
    public void testUsersOutsideRadius() {
        User user1 = new User(40.7128, -74.0060, 1);
        User user2 = new User(41.7128, -75.0060, 2);
        List<User> users = Arrays.asList(user1, user2);
        double radius = 10.0;
        
        OptimalMeetingPoint result = MeetingPoint.findOptimalMeetingPoint(users, radius);
        
        // Should return one of the users as meeting point
        assertTrue(result.getLatitude() == 40.7128 || result.getLatitude() == 41.7128);
        assertTrue(result.getTotalCommunicationCost() == 0.0);
    }

    @Test
    public void testMultipleClusters() {
        User user1 = new User(40.7128, -74.0060, 1);
        User user2 = new User(40.7138, -74.0050, 2);
        User user3 = new User(41.7128, -75.0060, 3);
        User user4 = new User(41.7138, -75.0050, 4);
        List<User> users = Arrays.asList(user1, user2, user3, user4);
        double radius = 1.5;
        
        OptimalMeetingPoint result = MeetingPoint.findOptimalMeetingPoint(users, radius);
        
        // Should find optimal point in one of the clusters
        assertTrue(result.getTotalCommunicationCost() > 0);
    }

    @Test
    public void testAllSameLocation() {
        User user1 = new User(40.7128, -74.0060, 1);
        User user2 = new User(40.7128, -74.0060, 2);
        User user3 = new User(40.7128, -74.0060, 3);
        List<User> users = Arrays.asList(user1, user2, user3);
        double radius = 10.0;
        
        OptimalMeetingPoint result = MeetingPoint.findOptimalMeetingPoint(users, radius);
        
        assertEquals(40.7128, result.getLatitude(), DELTA);
        assertEquals(-74.0060, result.getLongitude(), DELTA);
        assertEquals(0.0, result.getTotalCommunicationCost(), DELTA);
    }

    @Test
    public void testEmptyUserList() {
        List<User> users = Arrays.asList();
        double radius = 10.0;
        
        assertThrows(IllegalArgumentException.class, () -> {
            MeetingPoint.findOptimalMeetingPoint(users, radius);
        });
    }

    @Test
    public void testNegativeRadius() {
        User user = new User(40.7128, -74.0060, 1);
        List<User> users = Arrays.asList(user);
        double radius = -1.0;
        
        assertThrows(IllegalArgumentException.class, () -> {
            MeetingPoint.findOptimalMeetingPoint(users, radius);
        });
    }
}