import java.util.*;

public class NetworkPartitioner {
    public static Map<Integer, Integer> partition(Node[] nodes, Edge[] edges, int k, int subnetworkDataCapacity, int subnetworkProcessingCapacity) {
        Map<Integer, Node> nodeMap = new HashMap<>();
        for (Node node : nodes) {
            nodeMap.put(node.id, node);
        }
        
        Map<Integer, List<Edge>> adj = new HashMap<>();
        for (Node node : nodes) {
            adj.put(node.id, new ArrayList<>());
        }
        for (Edge edge : edges) {
            if (adj.containsKey(edge.node1Id)) {
                adj.get(edge.node1Id).add(edge);
            }
            if (adj.containsKey(edge.node2Id)) {
                adj.get(edge.node2Id).add(edge);
            }
        }
        
        int[] leftData = new int[k];
        int[] leftProcessing = new int[k];
        Arrays.fill(leftData, subnetworkDataCapacity);
        Arrays.fill(leftProcessing, subnetworkProcessingCapacity);
        
        Map<Integer, Integer> assignment = new HashMap<>();
        
        List<Node> nodeList = new ArrayList<>(Arrays.asList(nodes));
        nodeList.sort((a, b) -> {
            int sumA = 0;
            int sumB = 0;
            for (Edge e : adj.get(a.id)) {
                sumA += e.dataTransferSize;
            }
            for (Edge e : adj.get(b.id)) {
                sumB += e.dataTransferSize;
            }
            return sumB - sumA;
        });
        
        for (Node node : nodeList) {
            int bestPartition = -1;
            int bestCost = Integer.MAX_VALUE;
            boolean found = false;
            for (int p = 0; p < k; p++) {
                if (leftData[p] < node.dataSize || leftProcessing[p] < node.processingCapacity) {
                    continue;
                }
                int cost = 0;
                for (Edge edge : adj.get(node.id)) {
                    int neighborId = (edge.node1Id == node.id) ? edge.node2Id : edge.node1Id;
                    if (assignment.containsKey(neighborId)) {
                        int neighborPartition = assignment.get(neighborId);
                        if (neighborPartition != p) {
                            cost += edge.dataTransferSize;
                        }
                    }
                }
                if (cost < bestCost) {
                    bestCost = cost;
                    bestPartition = p;
                    found = true;
                }
            }
            if (!found) {
                return null;
            }
            assignment.put(node.id, bestPartition);
            leftData[bestPartition] -= node.dataSize;
            leftProcessing[bestPartition] -= node.processingCapacity;
        }
        
        return assignment;
    }
}