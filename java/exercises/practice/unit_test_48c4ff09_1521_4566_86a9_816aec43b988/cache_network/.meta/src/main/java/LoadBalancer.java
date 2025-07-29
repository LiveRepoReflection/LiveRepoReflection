import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class LoadBalancer {
    private final List<CacheNode> nodes;
    private final int[][] latencies;
    private final int originLatency;
    private final Random random;
    
    public LoadBalancer(List<CacheNode> nodes, int[][] latencies, int originLatency) {
        this.nodes = nodes;
        this.latencies = latencies;
        this.originLatency = originLatency;
        this.random = new Random();
    }
    
    public double processRequests(int[] requests) {
        double totalLatency = 0;
        
        for (int item : requests) {
            // Simple round-robin strategy (can be replaced with more sophisticated algorithm)
            int nodeIndex = random.nextInt(nodes.size());
            CacheNode selectedNode = nodes.get(nodeIndex);
            
            int nodeLatency = latencies[0][selectedNode.getNodeId()];
            int processingLatency = selectedNode.processRequest(item, originLatency);
            
            totalLatency += nodeLatency + processingLatency;
        }
        
        return totalLatency / requests.length;
    }
}