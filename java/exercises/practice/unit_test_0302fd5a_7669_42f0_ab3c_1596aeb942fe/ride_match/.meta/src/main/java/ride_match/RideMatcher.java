package ride_match;

import ride_match.model.Rider;
import ride_match.model.Driver;
import java.util.List;

public class RideMatcher {
    public static Driver matchRider(Rider rider, List<Driver> drivers) {
        Driver bestMatch = null;
        double bestDistance = Double.MAX_VALUE;
        for (Driver driver : drivers) {
            if (driver.getCapacity() < rider.getRequiredCapacity()) {
                continue;
            }
            if (driver.getAvailableStart() > rider.getPickupStart() || driver.getAvailableEnd() < rider.getPickupEnd()) {
                continue;
            }
            double distance = calculateDistance(rider.getOriginLatitude(), rider.getOriginLongitude(),
                                                driver.getLatitude(), driver.getLongitude());
            if (distance < bestDistance) {
                bestDistance = distance;
                bestMatch = driver;
            } else if (distance == bestDistance && bestMatch != null) {
                if (driver.getDriverScore() > bestMatch.getDriverScore()) {
                    bestMatch = driver;
                }
            }
        }
        return bestMatch;
    }
    
    private static double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        double dLat = lat1 - lat2;
        double dLon = lon1 - lon2;
        return Math.sqrt(dLat * dLat + dLon * dLon);
    }
}