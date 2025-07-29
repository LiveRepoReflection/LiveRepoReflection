import java.util.List;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

public class MeetingPoint {
    private static final double EARTH_RADIUS = 6371.0; // Earth's radius in km
    private static final int MAX_ITERATIONS = 100;
    private static final double CONVERGENCE_THRESHOLD = 0.0001;

    public static OptimalMeetingPoint findOptimalMeetingPoint(List<User> users, double radius) {
        if (users == null || users.isEmpty()) {
            throw new IllegalArgumentException("User list cannot be null or empty");
        }
        if (radius <= 0) {
            throw new IllegalArgumentException("Radius must be positive");
        }

        // Find connected components (clusters) of users within communication radius
        List<Set<User>> clusters = findClusters(users, radius);

        // If no clusters found (all users isolated), return first user's location
        if (clusters.isEmpty()) {
            return new OptimalMeetingPoint(
                users.get(0).getLatitude(),
                users.get(0).getLongitude(),
                0.0
            );
        }

        // Find the largest cluster
        Set<User> largestCluster = findLargestCluster(clusters);

        // Calculate geometric median for the largest cluster
        return calculateGeometricMedian(largestCluster);
    }

    private static List<Set<User>> findClusters(List<User> users, double radius) {
        List<Set<User>> clusters = new ArrayList<>();
        Set<User> visited = new HashSet<>();

        for (User user : users) {
            if (!visited.contains(user)) {
                Set<User> cluster = new HashSet<>();
                dfs(user, users, radius, cluster, visited);
                if (cluster.size() > 1) { // Only consider clusters with at least 2 users
                    clusters.add(cluster);
                }
            }
        }

        return clusters;
    }

    private static void dfs(User current, List<User> users, double radius, 
                          Set<User> cluster, Set<User> visited) {
        visited.add(current);
        cluster.add(current);

        for (User neighbor : users) {
            if (!visited.contains(neighbor) && 
                haversineDistance(current, neighbor) <= radius) {
                dfs(neighbor, users, radius, cluster, visited);
            }
        }
    }

    private static Set<User> findLargestCluster(List<Set<User>> clusters) {
        Set<User> largest = new HashSet<>();
        for (Set<User> cluster : clusters) {
            if (cluster.size() > largest.size()) {
                largest = cluster;
            }
        }
        return largest;
    }

    private static OptimalMeetingPoint calculateGeometricMedian(Set<User> cluster) {
        // Initialize with centroid
        double currentLat = 0;
        double currentLon = 0;
        for (User user : cluster) {
            currentLat += user.getLatitude();
            currentLon += user.getLongitude();
        }
        currentLat /= cluster.size();
        currentLon /= cluster.size();

        // Weiszfeld's algorithm for geometric median
        for (int i = 0; i < MAX_ITERATIONS; i++) {
            double sumWeights = 0;
            double sumWeightedLat = 0;
            double sumWeightedLon = 0;
            double totalCost = 0;

            for (User user : cluster) {
                double distance = haversineDistance(currentLat, currentLon, 
                                                  user.getLatitude(), user.getLongitude());
                if (distance == 0) continue; // avoid division by zero
                double weight = 1 / distance;
                sumWeights += weight;
                sumWeightedLat += weight * user.getLatitude();
                sumWeightedLon += weight * user.getLongitude();
                totalCost += distance;
            }

            if (sumWeights == 0) break; // all points are the same

            double newLat = sumWeightedLat / sumWeights;
            double newLon = sumWeightedLon / sumWeights;

            // Check for convergence
            if (haversineDistance(currentLat, currentLon, newLat, newLon) < CONVERGENCE_THRESHOLD) {
                currentLat = newLat;
                currentLon = newLon;
                break;
            }

            currentLat = newLat;
            currentLon = newLon;
        }

        // Calculate final total communication cost
        double totalCost = 0;
        for (User user : cluster) {
            totalCost += haversineDistance(currentLat, currentLon, 
                                         user.getLatitude(), user.getLongitude());
        }

        return new OptimalMeetingPoint(currentLat, currentLon, totalCost);
    }

    private static double haversineDistance(User a, User b) {
        return haversineDistance(a.getLatitude(), a.getLongitude(), 
                               b.getLatitude(), b.getLongitude());
    }

    private static double haversineDistance(double lat1, double lon1, double lat2, double lon2) {
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        lat1 = Math.toRadians(lat1);
        lat2 = Math.toRadians(lat2);

        double a = Math.pow(Math.sin(dLat / 2), 2) + 
                   Math.pow(Math.sin(dLon / 2), 2) * Math.cos(lat1) * Math.cos(lat2);
        double c = 2 * Math.asin(Math.sqrt(a));
        return EARTH_RADIUS * c;
    }
}