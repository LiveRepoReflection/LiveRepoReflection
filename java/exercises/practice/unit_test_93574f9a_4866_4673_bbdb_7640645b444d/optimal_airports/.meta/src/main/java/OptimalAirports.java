import java.util.*;

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
        int n = locations.size();
        
        // Special case: If K equals N, select all locations
        if (K >= n) {
            List<Integer> allIndices = new ArrayList<>();
            for (int i = 0; i < n; i++) {
                allIndices.add(i);
            }
            return allIndices;
        }

        // Special case: If K is 1, select the location that minimizes the maximum distance
        if (K == 1) {
            int bestCenterId = -1;
            double minMaxDistance = Double.MAX_VALUE;

            for (int i = 0; i < n; i++) {
                double maxDistance = 0;
                for (int j = 0; j < n; j++) {
                    if (i != j) {
                        double dist = distance(locations.get(i), locations.get(j));
                        maxDistance = Math.max(maxDistance, dist);
                    }
                }
                if (maxDistance < minMaxDistance) {
                    minMaxDistance = maxDistance;
                    bestCenterId = i;
                }
            }
            return Collections.singletonList(bestCenterId);
        }

        // For K >= 2 and K < N, we use a combination of approaches:
        // 1. Greedy algorithm as a starting point
        // 2. Local search to improve the solution
        
        // Precompute the distance matrix for efficiency
        double[][] distMatrix = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                distMatrix[i][j] = distance(locations.get(i), locations.get(j));
                distMatrix[j][i] = distMatrix[i][j];
            }
        }

        // Initialize solution with greedy algorithm
        Set<Integer> selected = greedySelection(distMatrix, n, K);
        
        // Use local search to improve the solution
        Set<Integer> bestSelection = localSearch(distMatrix, n, K, selected);
        
        // Convert set to list for return
        return new ArrayList<>(bestSelection);
    }
    
    /**
     * Greedy initialization: Start with most distant location pairs
     */
    private Set<Integer> greedySelection(double[][] distMatrix, int n, int K) {
        Set<Integer> selected = new HashSet<>();
        
        // Find the two most distant locations as initial airports
        double maxDist = -1;
        int first = 0, second = 0;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (distMatrix[i][j] > maxDist) {
                    maxDist = distMatrix[i][j];
                    first = i;
                    second = j;
                }
            }
        }
        selected.add(first);
        selected.add(second);
        
        // Add remaining airports greedily
        while (selected.size() < K) {
            int bestLocation = -1;
            double minMaxDist = Double.MAX_VALUE;
            
            for (int i = 0; i < n; i++) {
                if (!selected.contains(i)) {
                    // Find max distance from this location to any location if this location was added
                    double maxDistance = evaluateMaxDistance(distMatrix, n, selected, i);
                    
                    if (maxDistance < minMaxDist) {
                        minMaxDist = maxDistance;
                        bestLocation = i;
                    }
                }
            }
            
            selected.add(bestLocation);
        }
        
        return selected;
    }
    
    /**
     * Local search to improve the solution
     */
    private Set<Integer> localSearch(double[][] distMatrix, int n, int K, Set<Integer> initialSelection) {
        Set<Integer> currentSelection = new HashSet<>(initialSelection);
        double currentCost = evaluateMaxDistance(distMatrix, n, currentSelection, -1);
        boolean improved = true;
        
        // Continue until no more improvements can be made
        while (improved) {
            improved = false;
            
            // Try to swap each selected location with each unselected location
            for (int selected : new HashSet<>(currentSelection)) {
                for (int i = 0; i < n; i++) {
                    if (!currentSelection.contains(i)) {
                        // Try swapping selected with i
                        currentSelection.remove(selected);
                        currentSelection.add(i);
                        
                        double newCost = evaluateMaxDistance(distMatrix, n, currentSelection, -1);
                        
                        if (newCost < currentCost) {
                            // Keep the improvement
                            currentCost = newCost;
                            improved = true;
                        } else {
                            // Revert the swap
                            currentSelection.remove(i);
                            currentSelection.add(selected);
                        }
                    }
                }
            }
        }
        
        return currentSelection;
    }
    
    /**
     * Evaluate the maximum delivery time for a given selection of airports.
     * If candidateToAdd >= 0, it temporarily adds this candidate to the selection for evaluation.
     */
    private double evaluateMaxDistance(double[][] distMatrix, int n, Set<Integer> selected, int candidateToAdd) {
        // Create a temporary set with the candidate if provided
        Set<Integer> tempSelected = new HashSet<>(selected);
        if (candidateToAdd >= 0) {
            tempSelected.add(candidateToAdd);
        }
        
        // Floyd-Warshall algorithm to find all-pairs shortest paths
        double[][] shortestPaths = new double[n][n];
        
        // Initialize with infinite distances
        for (int i = 0; i < n; i++) {
            Arrays.fill(shortestPaths[i], Double.POSITIVE_INFINITY);
            shortestPaths[i][i] = 0; // Distance to self is 0
        }
        
        // Direct connections between airports
        for (int i : tempSelected) {
            for (int j : tempSelected) {
                shortestPaths[i][j] = distMatrix[i][j];
            }
        }
        
        // Floyd-Warshall algorithm to find shortest paths between all pairs of airports
        for (int k : tempSelected) {
            for (int i : tempSelected) {
                for (int j : tempSelected) {
                    if (shortestPaths[i][k] + shortestPaths[k][j] < shortestPaths[i][j]) {
                        shortestPaths[i][j] = shortestPaths[i][k] + shortestPaths[k][j];
                    }
                }
            }
        }
        
        // Calculate maximum delivery time considering all pairs of locations
        double maxDeliveryTime = 0;
        
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                // If both locations are not airports, we need to connect via airports
                if (!tempSelected.contains(i) && !tempSelected.contains(j)) {
                    // Find the closest airport to each location
                    double minDistI = Double.POSITIVE_INFINITY;
                    double minDistJ = Double.POSITIVE_INFINITY;
                    int closestToI = -1;
                    int closestToJ = -1;
                    
                    for (int airport : tempSelected) {
                        if (distMatrix[i][airport] < minDistI) {
                            minDistI = distMatrix[i][airport];
                            closestToI = airport;
                        }
                        if (distMatrix[j][airport] < minDistJ) {
                            minDistJ = distMatrix[j][airport];
                            closestToJ = airport;
                        }
                    }
                    
                    // Total delivery time is: dist(i -> closest airport to i) + 
                    // shortest path between airports + dist(closest airport to j -> j)
                    double deliveryTime = minDistI + shortestPaths[closestToI][closestToJ] + minDistJ;
                    maxDeliveryTime = Math.max(maxDeliveryTime, deliveryTime);
                }
                // If at least one is an airport
                else if (!tempSelected.contains(i)) {
                    // i is not an airport, but j is
                    double deliveryTime = distMatrix[i][j];
                    maxDeliveryTime = Math.max(maxDeliveryTime, deliveryTime);
                }
                else if (!tempSelected.contains(j)) {
                    // j is not an airport, but i is
                    double deliveryTime = distMatrix[i][j];
                    maxDeliveryTime = Math.max(maxDeliveryTime, deliveryTime);
                }
                // Both are airports - direct connection
                else {
                    double deliveryTime = distMatrix[i][j];
                    maxDeliveryTime = Math.max(maxDeliveryTime, deliveryTime);
                }
            }
        }
        
        return maxDeliveryTime;
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