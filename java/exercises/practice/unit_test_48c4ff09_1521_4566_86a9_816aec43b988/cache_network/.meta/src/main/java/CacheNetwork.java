import java.util.ArrayList;
import java.util.List;

public class CacheNetwork {
    public static void main(String[] args) {
        // Example configuration
        int N = 3;
        int[] capacities = {10, 5, 8};
        int[][] latencies = {{10, 15, 20}, {15, 8, 12}, {20, 12, 5}};
        int originLatency = 50;
        int[] requests = {1, 2, 1, 3, 2, 4, 1, 5, 6, 2};
        
        // Create cache nodes
        List<CacheNode> nodes = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            nodes.add(new CacheNode(capacities[i], i));
        }
        
        // Create load balancer
        LoadBalancer loadBalancer = new LoadBalancer(nodes, latencies, originLatency);
        
        // Process requests
        double averageLatency = loadBalancer.processRequests(requests);
        System.out.println("Average latency: " + averageLatency);
    }
}