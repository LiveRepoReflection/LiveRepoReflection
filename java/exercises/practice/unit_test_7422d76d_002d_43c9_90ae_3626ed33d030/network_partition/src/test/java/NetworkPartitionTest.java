import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

public class NetworkPartitionTest {

    @Test
    public void testSinglePartition() {
        Node[] nodes = new Node[] {
            new Node(1, 50, 4),
            new Node(2, 30, 2),
            new Node(3, 20, 1)
        };
        Edge[] edges = new Edge[] {
            new Edge(1, 2, 10),
            new Edge(2, 3, 20)
        };
        int k = 1;
        int subnetworkDataCapacity = 200;
        int subnetworkProcessingCapacity = 10;
        Map<Integer, Integer> result = NetworkPartitioner.partition(nodes, edges, k, subnetworkDataCapacity, subnetworkProcessingCapacity);
        assertNotNull(result, "Expected non-null partition for k=1");
        for (int nodeId : result.keySet()) {
            assertEquals(0, result.get(nodeId), "All nodes should be in partition 0");
        }
    }

    @Test
    public void testSimplePartition() {
        Node[] nodes = new Node[] {
            new Node(1, 40, 3),
            new Node(2, 30, 2),
            new Node(3, 20, 1),
            new Node(4, 50, 4)
        };
        Edge[] edges = new Edge[] {
            new Edge(1, 2, 15),
            new Edge(1, 3, 20),
            new Edge(2, 4, 25),
            new Edge(3, 4, 30)
        };
        int k = 2;
        int subnetworkDataCapacity = 100;
        int subnetworkProcessingCapacity = 7;
        Map<Integer, Integer> result = NetworkPartitioner.partition(nodes, edges, k, subnetworkDataCapacity, subnetworkProcessingCapacity);
        assertNotNull(result, "Partitioning should be possible");
        assertEquals(4, result.size(), "Expected partition mapping for all nodes");
        Map<Integer, Integer> dataSum = new HashMap<>();
        Map<Integer, Integer> procSum = new HashMap<>();
        for (Node n : nodes) {
            int part = result.get(n.id);
            dataSum.put(part, dataSum.getOrDefault(part, 0) + n.dataSize);
            procSum.put(part, procSum.getOrDefault(part, 0) + n.processingCapacity);
        }
        for (Integer part : dataSum.keySet()) {
            assertTrue(dataSum.get(part) <= subnetworkDataCapacity, "Data capacity exceeded in partition " + part);
            assertTrue(procSum.get(part) <= subnetworkProcessingCapacity, "Processing capacity exceeded in partition " + part);
        }
    }

    @Test
    public void testDisconnectedGraph() {
        Node[] nodes = new Node[] {
            new Node(1, 10, 1),
            new Node(2, 20, 2),
            new Node(3, 15, 1),
            new Node(4, 25, 2)
        };
        Edge[] edges = new Edge[] {
            new Edge(1, 2, 10),
            new Edge(3, 4, 20)
        };
        int k = 2;
        int subnetworkDataCapacity = 50;
        int subnetworkProcessingCapacity = 5;
        Map<Integer, Integer> result = NetworkPartitioner.partition(nodes, edges, k, subnetworkDataCapacity, subnetworkProcessingCapacity);
        assertNotNull(result, "Partitioning should be possible for disconnected graph");
        for (Integer nodeId : result.keySet()) {
            int part = result.get(nodeId);
            assertTrue(part >= 0 && part < k, "Partition id must be in range");
        }
    }

    @Test
    public void testImpossiblePartition() {
        Node[] nodes = new Node[] {
            new Node(1, 150, 5),
            new Node(2, 150, 5)
        };
        Edge[] edges = new Edge[] {
            new Edge(1, 2, 50)
        };
        int k = 2;
        int subnetworkDataCapacity = 100;
        int subnetworkProcessingCapacity = 10;
        Map<Integer, Integer> result = NetworkPartitioner.partition(nodes, edges, k, subnetworkDataCapacity, subnetworkProcessingCapacity);
        assertNull(result, "Expected null partitioning when capacity constraints cannot be met");
    }

    @Test
    public void testEachNodeSeparately() {
        Node[] nodes = new Node[] {
            new Node(1, 20, 1),
            new Node(2, 30, 2),
            new Node(3, 25, 1),
            new Node(4, 15, 1)
        };
        Edge[] edges = new Edge[] {
            new Edge(1, 2, 10),
            new Edge(2, 3, 10),
            new Edge(3, 4, 10),
            new Edge(4, 1, 10)
        };
        int k = nodes.length;
        int subnetworkDataCapacity = 50;
        int subnetworkProcessingCapacity = 3;
        Map<Integer, Integer> result = NetworkPartitioner.partition(nodes, edges, k, subnetworkDataCapacity, subnetworkProcessingCapacity);
        assertNotNull(result, "Partitioning should be possible for individual subnetwork per node");
        assertEquals(nodes.length, result.size(), "All nodes must have a partition assignment");
        for (Integer part : result.values()) {
            assertTrue(part >= 0 && part < k, "Partition id must be in range");
        }
    }
}