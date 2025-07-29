import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Disabled;

import java.util.*;
import static org.assertj.core.api.Assertions.assertThat;

public class OptimalAirportsTest {

    private OptimalAirports optimalAirports;

    @BeforeEach
    public void setup() {
        optimalAirports = new OptimalAirports();
    }

    @Test
    public void testDistanceCalculation() {
        // Los Angeles
        Pair<Double, Double> la = new Pair<>(34.0522, -118.2437);
        // New York
        Pair<Double, Double> ny = new Pair<>(40.7128, -74.0060);
        
        double distance = optimalAirports.distance(la, ny);
        // The approximate distance between LA and NY is ~3900 km
        assertThat(distance).isGreaterThan(3800).isLessThan(4000);
    }

    @Disabled("Remove to run test")
    @Test
    public void testSingleAirport() {
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // Los Angeles
        locations.add(new Pair<>(34.0522, -118.2437));
        // New York
        locations.add(new Pair<>(40.7128, -74.0060));
        // London
        locations.add(new Pair<>(51.5074, -0.1278));
        
        List<Integer> result = optimalAirports.findOptimalAirports(locations, 1);
        
        assertThat(result).hasSize(1);
        // When selecting a single airport, it should be the one that minimizes
        // the maximum distance to all other locations
        // This test doesn't check the exact optimal location since that would be complex,
        // just that it returns a valid single location
    }

    @Disabled("Remove to run test")
    @Test
    public void testAllLocationsAsAirports() {
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // Los Angeles
        locations.add(new Pair<>(34.0522, -118.2437));
        // New York
        locations.add(new Pair<>(40.7128, -74.0060));
        // London
        locations.add(new Pair<>(51.5074, -0.1278));
        
        List<Integer> result = optimalAirports.findOptimalAirports(locations, 3);
        
        // When K equals N, all locations should be selected
        assertThat(result).containsExactlyInAnyOrder(0, 1, 2);
    }

    @Disabled("Remove to run test")
    @Test
    public void testGlobalCoverage() {
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // Los Angeles
        locations.add(new Pair<>(34.0522, -118.2437));
        // New York
        locations.add(new Pair<>(40.7128, -74.0060));
        // London
        locations.add(new Pair<>(51.5074, -0.1278));
        // Tokyo
        locations.add(new Pair<>(35.6762, 139.6503));
        // Sydney
        locations.add(new Pair<>(-33.8688, 151.2093));
        // Rio de Janeiro
        locations.add(new Pair<>(-22.9068, -43.1729));
        // Cape Town
        locations.add(new Pair<>(-33.9249, 18.4241));
        
        List<Integer> result = optimalAirports.findOptimalAirports(locations, 3);
        
        // Check that the result has the correct size
        assertThat(result).hasSize(3);
        
        // All indices should be valid
        for (int idx : result) {
            assertThat(idx).isGreaterThanOrEqualTo(0).isLessThan(locations.size());
        }
        
        // All indices should be distinct
        assertThat(new HashSet<>(result)).hasSize(result.size());
    }

    @Disabled("Remove to run test")
    @Test
    public void testCloseLocations() {
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // New York City
        locations.add(new Pair<>(40.7128, -74.0060));
        // Newark (very close to NYC)
        locations.add(new Pair<>(40.7357, -74.1724));
        // Los Angeles
        locations.add(new Pair<>(34.0522, -118.2437));
        // Tokyo
        locations.add(new Pair<>(35.6762, 139.6503));
        
        List<Integer> result = optimalAirports.findOptimalAirports(locations, 2);
        
        // This test doesn't verify the exact solution, but checks basic properties
        assertThat(result).hasSize(2);
        assertThat(new HashSet<>(result)).hasSize(2); // No duplicates
    }

    @Disabled("Remove to run test")
    @Test
    public void testSmallExample() {
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // Los Angeles
        locations.add(new Pair<>(34.0522, -118.2437));
        // New York
        locations.add(new Pair<>(40.7128, -74.0060));
        // London
        locations.add(new Pair<>(51.5074, -0.1278));
        // Sydney
        locations.add(new Pair<>(-33.8688, 151.2093));
        
        int K = 2;
        List<Integer> result = optimalAirports.findOptimalAirports(locations, K);
        
        // Verify that the result has K elements
        assertThat(result).hasSize(K);
        
        // Verify that the indices are within bounds
        for (int idx : result) {
            assertThat(idx).isGreaterThanOrEqualTo(0).isLessThan(locations.size());
        }
        
        // Verify that all indices are unique
        assertThat(new HashSet<>(result)).hasSize(K);
    }

    @Disabled("Remove to run test")
    @Test
    public void testPerturbedInput() {
        List<Pair<Double, Double>> originalLocations = new ArrayList<>();
        // Los Angeles
        originalLocations.add(new Pair<>(34.0522, -118.2437));
        // New York
        originalLocations.add(new Pair<>(40.7128, -74.0060));
        // London
        originalLocations.add(new Pair<>(51.5074, -0.1278));
        // Tokyo
        originalLocations.add(new Pair<>(35.6762, 139.6503));
        
        // Create a slightly perturbed version (small random shifts)
        Random random = new Random(42); // Fixed seed for reproducibility
        List<Pair<Double, Double>> perturbedLocations = new ArrayList<>();
        for (Pair<Double, Double> loc : originalLocations) {
            // Add small perturbation (±0.0001 degrees, which is ~10 meters)
            double perturbedLat = loc.getFirst() + (random.nextDouble() - 0.5) * 0.0002;
            double perturbedLon = loc.getSecond() + (random.nextDouble() - 0.5) * 0.0002;
            perturbedLocations.add(new Pair<>(perturbedLat, perturbedLon));
        }
        
        // The optimal solution should be similar for both inputs
        List<Integer> originalResult = optimalAirports.findOptimalAirports(originalLocations, 2);
        List<Integer> perturbedResult = optimalAirports.findOptimalAirports(perturbedLocations, 2);
        
        // We can't assert that they're exactly equal because small perturbations might
        // change the optimal solution in boundary cases, but we check basic properties
        assertThat(originalResult).hasSize(2);
        assertThat(perturbedResult).hasSize(2);
    }

    @Disabled("Remove to run test")
    @Test
    public void testLargerInput() {
        // Create a larger test case with 15 locations
        List<Pair<Double, Double>> locations = new ArrayList<>();
        // Major world cities at approximate coordinates
        locations.add(new Pair<>(34.0522, -118.2437)); // Los Angeles
        locations.add(new Pair<>(40.7128, -74.0060));  // New York
        locations.add(new Pair<>(51.5074, -0.1278));   // London
        locations.add(new Pair<>(48.8566, 2.3522));    // Paris
        locations.add(new Pair<>(55.7558, 37.6173));   // Moscow
        locations.add(new Pair<>(35.6762, 139.6503));  // Tokyo
        locations.add(new Pair<>(22.3193, 114.1694));  // Hong Kong
        locations.add(new Pair<>(1.3521, 103.8198));   // Singapore
        locations.add(new Pair<>(-33.8688, 151.2093)); // Sydney
        locations.add(new Pair<>(-22.9068, -43.1729)); // Rio de Janeiro
        locations.add(new Pair<>(-34.6037, -58.3816)); // Buenos Aires
        locations.add(new Pair<>(25.2048, 55.2708));   // Dubai
        locations.add(new Pair<>(-1.2921, 36.8219));   // Nairobi
        locations.add(new Pair<>(-33.9249, 18.4241));  // Cape Town
        locations.add(new Pair<>(37.7749, -122.4194)); // San Francisco
        
        // Select 5 optimal airports
        List<Integer> result = optimalAirports.findOptimalAirports(locations, 5);
        
        // Verify basic properties
        assertThat(result).hasSize(5);
        for (int idx : result) {
            assertThat(idx).isGreaterThanOrEqualTo(0).isLessThan(locations.size());
        }
        assertThat(new HashSet<>(result)).hasSize(5); // No duplicates
    }
}