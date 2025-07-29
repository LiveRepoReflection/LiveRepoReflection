import java.util.List;

/**
 * Interface defining the operations required for the Network Paths problem
 */
public interface NetworkPathsInterface {
    
    /**
     * Updates the latency of an edge in the network
     * 
     * @param source The source node
     * @param destination The destination node
     * @param newLatency The new latency value
     */
    void updateLatency(int source, int destination, int newLatency);
    
    /**
     * Finds the k shortest paths from source to destination
     * 
     * @param source The source node
     * @param destination The destination node
     * @param k The number of paths to find
     * @return A list of paths, where each path is a list of node IDs
     */
    List<List<Integer>> findShortestPaths(int source, int destination, int k);
}