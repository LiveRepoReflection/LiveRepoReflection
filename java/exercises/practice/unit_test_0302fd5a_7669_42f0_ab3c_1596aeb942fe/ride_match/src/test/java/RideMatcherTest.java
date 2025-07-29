import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;
import ride_match.RideMatcher;
import ride_match.model.Rider;
import ride_match.model.Driver;

public class RideMatcherTest {

    @Test
    public void testNoDriversAvailable() {
        // Create a rider with pickup time window 0 to 10 minutes.
        Rider rider = new Rider("rider1", 40.7128, -74.0060, 40.730610, -73.935242, 0, 10, 1);
        List<Driver> drivers = new ArrayList<>();
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNull(match, "Expected no match when no drivers are available.");
    }

    @Test
    public void testSingleDriverMatch() {
        // Rider with pickup time window from 5 to 15 minutes and requires capacity 1.
        Rider rider = new Rider("rider2", 37.7749, -122.4194, 37.8044, -122.2711, 5, 15, 1);
        // Driver available in the same time window and sufficient capacity.
        Driver driver = new Driver("driver1", 37.7750, -122.4195, 4, 90, 5, 15);
        List<Driver> drivers = Arrays.asList(driver);
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNotNull(match, "Expected a matching driver to be found.");
        assertEquals("driver1", match.getId(), "Expected driver1 to be matched.");
    }

    @Test
    public void testMultipleDriversMatch() {
        // Rider with pickup time window from 10 to 20 minutes and requires capacity 2.
        Rider rider = new Rider("rider3", 34.0522, -118.2437, 34.0522, -118.2437, 10, 20, 2);
        // Driver with higher driver score but slightly further.
        Driver driver1 = new Driver("driver1", 34.0700, -118.2500, 4, 95, 10, 20);
        // Driver with lower driver score but significantly closer.
        Driver driver2 = new Driver("driver2", 34.0525, -118.2439, 4, 85, 10, 20);
        List<Driver> drivers = Arrays.asList(driver1, driver2);
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNotNull(match, "Expected a matching driver to be found.");
        // According to criteria, driver2 should be chosen because of proximity.
        assertEquals("driver2", match.getId(), "Expected driver2 to be matched due to better proximity.");
    }

    @Test
    public void testTimeWindowMismatch() {
        // Rider with pickup time window of 15 to 25 minutes.
        Rider rider = new Rider("rider4", 51.5074, -0.1278, 51.509865, -0.118092, 15, 25, 1);
        // Driver available only between 0 to 10 minutes.
        Driver driver = new Driver("driver1", 51.5075, -0.1279, 4, 80, 0, 10);
        List<Driver> drivers = Arrays.asList(driver);
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNull(match, "Expected no match when driver's time availability does not match rider's time window.");
    }

    @Test
    public void testRidePreferenceMismatch() {
        // Rider requires a capacity of 2.
        Rider rider = new Rider("rider5", 48.8566, 2.3522, 48.864716, 2.349014, 5, 15, 2);
        // Driver's vehicle capacity is only 1.
        Driver driver = new Driver("driver1", 48.8567, 2.3523, 1, 90, 5, 15);
        List<Driver> drivers = Arrays.asList(driver);
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNull(match, "Expected no match due to ride preference mismatch in vehicle capacity.");
    }

    @Test
    public void testEdgeCaseExactMatchOnBoundaries() {
        // Rider pickup window exactly aligns with driver's available window.
        Rider rider = new Rider("rider6", 35.6895, 139.6917, 35.6897, 139.6920, 10, 20, 1);
        Driver driver = new Driver("driver1", 35.6896, 139.6918, 4, 88, 10, 20);
        List<Driver> drivers = Arrays.asList(driver);
        Driver match = RideMatcher.matchRider(rider, drivers);
        assertNotNull(match, "Expected a match when driver's availability exactly aligns with the rider's time window.");
        assertEquals("driver1", match.getId(), "Expected driver1 to be matched under exact boundary conditions.");
    }
}