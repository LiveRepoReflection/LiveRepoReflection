import java.util.*;

public class NetworkLatency {
    private final int nodeCount;
    private final List<List<int[]>> adjacencyList;
    private int[][] distanceMatrix;
    private boolean needsRebuild;

    public NetworkLatency(int nodeCount) {
        if (nodeCount <= 0) {
            throw new IllegalArgumentException("Node count must be positive");
        }
        this.nodeCount = nodeCount;
        this.adjacencyList = new ArrayList<>(nodeCount);
        for (int i = 0; i < nodeCount; i++) {
            adjacencyList.add(new ArrayList<>());
        }
        this.distanceMatrix = new int[nodeCount][nodeCount];
        this.needsRebuild = true;
        initializeDistanceMatrix();
    }

    private void initializeDistanceMatrix() {
        for (int i = 0; i < nodeCount; i++) {
            Arrays.fill(distanceMatrix[i], Integer.MAX_VALUE);
            distanceMatrix[i][i] = 0;
        }
    }

    public void addLink(int source, int destination, int latency) {
        validateNodes(source, destination);
        if (latency < 0) {
            throw new IllegalArgumentException("Latency must be non-negative");
        }

        List<int[]> edges = adjacencyList.get(source);
        for (int[] edge : edges) {
            if (edge[0] == destination) {
                edge[1] = latency;
                needsRebuild = true;
                return;
            }
        }
        edges.add(new int[]{destination, latency});
        needsRebuild = true;
    }

    public void removeLink(int source, int destination) {
        validateNodes(source, destination);
        List<int[]> edges = adjacencyList.get(source);
        edges.removeIf(edge -> edge[0] == destination);
        needsRebuild = true;
    }

    public int getMinLatency(int source, int destination) {
        validateNodes(source, destination);
        if (needsRebuild) {
            rebuildDistanceMatrix();
        }
        return distanceMatrix[source][destination] == Integer.MAX_VALUE ? 
               -1 : distanceMatrix[source][destination];
    }

    public Set<Integer> getNodesReachableWithinLatency(int source, int maxLatency) {
        validateNodes(source);
        if (maxLatency < 0) {
            throw new IllegalArgumentException("Max latency must be non-negative");
        }

        if (needsRebuild) {
            rebuildDistanceMatrix();
        }

        Set<Integer> reachableNodes = new TreeSet<>();
        for (int i = 0; i < nodeCount; i++) {
            if (distanceMatrix[source][i] <= maxLatency) {
                reachableNodes.add(i);
            }
        }
        return reachableNodes;
    }

    private void rebuildDistanceMatrix() {
        initializeDistanceMatrix();
        
        for (int i = 0; i < nodeCount; i++) {
            List<int[]> edges = adjacencyList.get(i);
            for (int[] edge : edges) {
                int destination = edge[0];
                int latency = edge[1];
                if (latency < distanceMatrix[i][destination]) {
                    distanceMatrix[i][destination] = latency;
                }
            }
        }

        for (int k = 0; k < nodeCount; k++) {
            for (int i = 0; i < nodeCount; i++) {
                if (distanceMatrix[i][k] == Integer.MAX_VALUE) continue;
                for (int j = 0; j < nodeCount; j++) {
                    if (distanceMatrix[k][j] == Integer.MAX_VALUE) continue;
                    if (distanceMatrix[i][j] > distanceMatrix[i][k] + distanceMatrix[k][j]) {
                        distanceMatrix[i][j] = distanceMatrix[i][k] + distanceMatrix[k][j];
                    }
                }
            }
        }
        needsRebuild = false;
    }

    private void validateNodes(int... nodes) {
        for (int node : nodes) {
            if (node < 0 || node >= nodeCount) {
                throw new IllegalArgumentException("Node ID out of bounds");
            }
        }
    }
}