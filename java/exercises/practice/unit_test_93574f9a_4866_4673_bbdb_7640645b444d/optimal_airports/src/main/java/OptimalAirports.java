import java.util.List;

/**
 * Class for finding the optimal airport locations to minimize the maximum delivery time
 * across a network of potential locations.
 */
public class OptimalAirports {

    /**
     * Finds the optimal set of K airports from the given list of locations to minimize
     * the maximum delivery time between any two locations in the network.
     *
     * @param locations List of location coordinates as pairs of latitude and longitude
     * @param K Number of airports to select
     * @return List of indices of the K selected airport locations that minimize the maximum delivery time
     */
    public List<Integer> findOptimalAirports(List<Pair<Double, Double>> locations, int K) {
        throw new UnsupportedOperationException("Implement this method");
    }

    /**
     * Calculates the great-circle distance between two locations on Earth.
     * 
     * @param location1 First location with latitude and longitude
     * @param location2 Second location with latitude and longitude
     * @return The distance in kilometers between the two locations
     */
    public double distance(Pair<Double, Double> location1, Pair<Double, Double> location2) {
        // Earth radius in kilometers
        final double EARTH_RADIUS = 6371.0;
        
        double lat1 = Math.toRadians(location1.getFirst());
        double lon1 = Math.toRadians(location1.getSecond());
        double lat2 = Math.toRadians(location2.getFirst());
        double lon2 = Math.toRadians(location2.getSecond());
        
        double dlon = lon2 - lon1;
        double dlat = lat2 - lat1;
        
        double a = Math.sin(dlat / 2) * Math.sin(dlat / 2) 
                 + Math.cos(lat1) * Math.cos(lat2) 
                 * Math.sin(dlon / 2) * Math.sin(dlon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return EARTH_RADIUS * c;
    }
}