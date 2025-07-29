import java.util.*;

public class TrafficSync {
    /**
     * Finds the optimal traffic light phase offsets to minimize average travel time across all intersections.
     *
     * @param N The number of intersections
     * @param adjList Adjacency list representing the city graph. adjList[i] contains pairs of 
     *        (destination intersection, travel time)
     * @param T The cycle time for all traffic lights
     * @param G The duration for which each traffic light is green
     * @return A list of phase offsets, one for each intersection
     */
    public List<Integer> findOptimalPhases(int N, List<List<Pair<Integer, Integer>>> adjList, int T, int G) {
        // Use simulated annealing to find near-optimal solution
        return simulatedAnnealing(N, adjList, T, G);
    }
    
    private List<Integer> simulatedAnnealing(int N, List<List<Pair<Integer, Integer>>> adjList, int T, int G) {
        Random random = new Random(42); // Use fixed seed for deterministic results
        
        // Initialize current solution with random phases
        List<Integer> currentSolution = new ArrayList<>(N);
        for (int i = 0; i < N; i++) {
            currentSolution.add(random.nextInt(T));
        }
        
        // Calculate initial average travel time
        double currentEnergy = evaluateSolution(currentSolution, N, adjList, T, G);
        
        List<Integer> bestSolution = new ArrayList<>(currentSolution);
        double bestEnergy = currentEnergy;
        
        // Simulated annealing parameters
        double temperature = 100.0;
        double coolingRate = 0.95;
        int iterations = 10000;
        
        // Main simulated annealing loop
        for (int i = 0; i < iterations; i++) {
            // Create a neighbor solution by changing one phase
            List<Integer> neighbor = new ArrayList<>(currentSolution);
            int intersectionToChange = random.nextInt(N);
            neighbor.set(intersectionToChange, random.nextInt(T));
            
            // Calculate neighbor energy
            double neighborEnergy = evaluateSolution(neighbor, N, adjList, T, G);
            
            // Decide whether to accept the new solution
            boolean accept = false;
            if (neighborEnergy < currentEnergy) {
                // Always accept better solutions
                accept = true;
            } else {
                // Accept worse solutions with a probability that decreases with temperature
                double acceptanceProbability = Math.exp((currentEnergy - neighborEnergy) / temperature);
                if (random.nextDouble() < acceptanceProbability) {
                    accept = true;
                }
            }
            
            if (accept) {
                currentSolution = neighbor;
                currentEnergy = neighborEnergy;
                
                // Update best solution if current one is better
                if (currentEnergy < bestEnergy) {
                    bestSolution = new ArrayList<>(currentSolution);
                    bestEnergy = currentEnergy;
                }
            }
            
            // Cool down the temperature
            temperature *= coolingRate;
        }
        
        return bestSolution;
    }
    
    private double evaluateSolution(List<Integer> phases, int N, List<List<Pair<Integer, Integer>>> adjList, int T, int G) {
        double totalTravelTime = 0.0;
        int validPairs = 0;
        
        for (int source = 0; source < N; source++) {
            for (int dest = 0; dest < N; dest++) {
                if (source != dest) {
                    double travelTime = calculateTravelTime(source, dest, phases, adjList, T, G);
                    
                    if (travelTime < Double.POSITIVE_INFINITY) {
                        totalTravelTime += travelTime;
                        validPairs++;
                    }
                }
            }
        }
        
        if (validPairs == 0) {
            return Double.POSITIVE_INFINITY; // No valid paths
        }
        
        return totalTravelTime / validPairs;
    }
    
    private double calculateTravelTime(int source, int dest, List<Integer> phases, 
                                     List<List<Pair<Integer, Integer>>> adjList, int T, int G) {
        int n = phases.size();
        double[] dist = new double[n];
        boolean[] visited = new boolean[n];
        
        // Initialize distances
        Arrays.fill(dist, Double.POSITIVE_INFINITY);
        dist[source] = 0.0;
        
        // Dijkstra's algorithm to find shortest path
        for (int i = 0; i < n; i++) {
            // Find the vertex with minimum distance
            int u = -1;
            double minDist = Double.POSITIVE_INFINITY;
            for (int v = 0; v < n; v++) {
                if (!visited[v] && dist[v] < minDist) {
                    u = v;
                    minDist = dist[v];
                }
            }
            
            if (u == -1 || u == dest) break; // No more reachable nodes or destination reached
            
            visited[u] = true;
            
            // Update distances to neighbors
            for (Pair<Integer, Integer> edge : adjList.get(u)) {
                int v = edge.getKey();
                int roadTime = edge.getValue();
                
                if (visited[v]) continue;
                
                // Calculate waiting time at traffic light v
                double arrivalTime = dist[u] + roadTime;
                double waitTime = calculateWaitTime(arrivalTime, phases.get(v), T, G);
                
                double newDist = arrivalTime + waitTime;
                
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                }
            }
        }
        
        return dist[dest];
    }
    
    private double calculateWaitTime(double arrivalTime, int phase, int T, int G) {
        // Calculate the current phase of the traffic light
        double cyclePosition = (arrivalTime % T);
        double greenStart = phase;
        double greenEnd = (phase + G) % T;
        
        if (greenStart < greenEnd) {
            // Light is green if cyclePosition is between greenStart and greenEnd
            if (cyclePosition >= greenStart && cyclePosition < greenEnd) {
                return 0.0; // Green light, no waiting
            } else if (cyclePosition < greenStart) {
                return greenStart - cyclePosition; // Wait until next green
            } else {
                return T - cyclePosition + greenStart; // Wait until green in next cycle
            }
        } else {
            // Green phase wraps around the cycle
            if (cyclePosition >= greenStart || cyclePosition < greenEnd) {
                return 0.0; // Green light, no waiting
            } else {
                return greenStart - cyclePosition; // Wait until next green
            }
        }
    }
}