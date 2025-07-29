import java.util.*;

public class NetworkReconstructionDemo {
    public static void main(String[] args) {
        // Example from the problem description
        int n = 4;
        List<LogEntry> log = Arrays.asList(
            new LogEntry(1678886400L, 1, 2),
            new LogEntry(1678886401L, 2, 3)
        );
        
        NetworkReconstruction networkReconstruction = new NetworkReconstruction();
        Map<Integer, Set<Integer>> result = networkReconstruction.reconstructNetwork(n, log);
        
        // Print the reconstructed network
        System.out.println("Reconstructed Network Topology:");
        for (int i = 1; i <= n; i++) {
            System.out.println("Server " + i + ": " + result.get(i));
        }
        
        // Calculate and print the average path length
        double avgPathLength = calculateAveragePathLength(result, n);
        System.out.println("\nAverage Path Length: " + avgPathLength);
    }
    
    // Helper method to calculate average path length in a graph
    private static double calculateAveragePathLength(Map<Integer, Set<Integer>> network, int n) {
        int totalPathLength = 0;
        int totalPaths = 0;
        
        // BFS from each node to find shortest paths
        for (int start = 1; start <= n; start++) {
            Queue<Integer> queue = new LinkedList<>();
            Map<Integer, Integer> distance = new HashMap<>();
            
            queue.add(start);
            distance.put(start, 0);
            
            while (!queue.isEmpty()) {
                int current = queue.poll();
                int currentDist = distance.get(current);
                
                for (int neighbor : network.get(current)) {
                    if (!distance.containsKey(neighbor)) {
                        distance.put(neighbor, currentDist + 1);
                        queue.add(neighbor);
                        totalPathLength += currentDist + 1;
                        totalPaths++;
                    }
                }
            }
        }
        
        return (double) totalPathLength / totalPaths;
    }
}