import java.util.Arrays;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        // Example usage of the NetworkPaths class
        int[][] edges = {
            {0, 1, 10},
            {0, 2, 5},
            {1, 2, 2},
            {2, 1, 3},
            {1, 3, 15},
            {2, 3, 7}
        };
        
        int n = 4; // Number of nodes
        double c = 0.1; // Congestion factor
        
        NetworkPaths network = new NetworkPaths(edges, n, c);
        
        // Initial query
        List<List<Integer>> paths1 = network.findShortestPaths(0, 3, 2);
        System.out.println("Initial Paths from 0 to 3:");
        printPaths(paths1);
        
        // Update edge latency
        network.updateLatency(0, 1, 8);
        System.out.println("\nAfter updating edge (0,1) to latency 8:");
        
        // Query again
        List<List<Integer>> paths2 = network.findShortestPaths(0, 3, 2);
        System.out.println("Paths from 0 to 3:");
        printPaths(paths2);
    }
    
    private static void printPaths(List<List<Integer>> paths) {
        if (paths.isEmpty()) {
            System.out.println("  No paths found");
            return;
        }
        
        for (int i = 0; i < paths.size(); i++) {
            System.out.println("  Path " + (i + 1) + ": " + paths.get(i));
        }
    }
}