import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class QosRoutingTest {

    @Test
    public void testBasicOptimalPath() {
        int numNodes = 4;
        List<QosRouting.Edge> edges = new ArrayList<>();
        edges.add(new QosRouting.Edge(0, 1, 100, 20, 10, 0.01, 5));
        edges.add(new QosRouting.Edge(0, 2, 80, 30, 15, 0.02, 8));
        edges.add(new QosRouting.Edge(1, 2, 70, 10, 5, 0.005, 3));
        edges.add(new QosRouting.Edge(1, 3, 90, 0, 20, 0.015, 10));
        edges.add(new QosRouting.Edge(2, 3, 60, 5, 12, 0.01, 6));

        int sourceNode = 0;
        int destinationNode = 3;
        int requiredBandwidth = 50;
        int maxLatency = 40;
        double maxPacketLossProbability = 0.03;

        // Optimal path should be [0, 2, 3] since it has a lower total cost.
        List<Integer> expected = Arrays.asList(0, 2, 3);
        List<Integer> result = QosRouting.findOptimalPath(numNodes, edges, sourceNode, destinationNode, requiredBandwidth, maxLatency, maxPacketLossProbability);
        assertEquals(expected, result);
    }

    @Test
    public void testNoValidPathDueToBandwidth() {
        int numNodes = 3;
        List<QosRouting.Edge> edges = new ArrayList<>();
        edges.add(new QosRouting.Edge(0, 1, 30, 10, 5, 0.01, 10));
        edges.add(new QosRouting.Edge(1, 2, 30, 10, 5, 0.01, 10));

        int sourceNode = 0;
        int destinationNode = 2;
        int requiredBandwidth = 25; // Each edge has effective bandwidth 20, which is insufficient.
        int maxLatency = 20;
        double maxPacketLossProbability = 0.05;

        List<Integer> expected = new ArrayList<>();
        List<Integer> result = QosRouting.findOptimalPath(numNodes, edges, sourceNode, destinationNode, requiredBandwidth, maxLatency, maxPacketLossProbability);
        assertEquals(expected, result);
    }

    @Test
    public void testSourceEqualsDestination() {
        int numNodes = 1;
        List<QosRouting.Edge> edges = new ArrayList<>();
        int sourceNode = 0;
        int destinationNode = 0;
        int requiredBandwidth = 10;
        int maxLatency = 10;
        double maxPacketLossProbability = 0.01;

        // When source and destination are the same the optimal path is the node itself.
        List<Integer> expected = Arrays.asList(0);
        List<Integer> result = QosRouting.findOptimalPath(numNodes, edges, sourceNode, destinationNode, requiredBandwidth, maxLatency, maxPacketLossProbability);
        assertEquals(expected, result);
    }

    @Test
    public void testGraphWithCycle() {
        int numNodes = 4;
        List<QosRouting.Edge> edges = new ArrayList<>();
        // Create a cycle: 0->1->2->0 and an extra edge 1->3.
        edges.add(new QosRouting.Edge(0, 1, 100, 10, 10, 0.01, 5));
        edges.add(new QosRouting.Edge(1, 2, 100, 10, 10, 0.01, 5));
        edges.add(new QosRouting.Edge(2, 0, 100, 10, 10, 0.01, 5));
        edges.add(new QosRouting.Edge(1, 3, 100, 10, 5, 0.01, 10));

        int sourceNode = 0;
        int destinationNode = 3;
        int requiredBandwidth = 80;
        int maxLatency = 50;
        double maxPacketLossProbability = 0.05;
        // Expected optimal path is 0 -> 1 -> 3.
        List<Integer> expected = Arrays.asList(0, 1, 3);
        List<Integer> result = QosRouting.findOptimalPath(numNodes, edges, sourceNode, destinationNode, requiredBandwidth, maxLatency, maxPacketLossProbability);
        assertEquals(expected, result);
    }

    @Test
    public void testFloatingPointImprecision() {
        int numNodes = 3;
        List<QosRouting.Edge> edges = new ArrayList<>();
        // Edges with extremely small packet loss probabilities.
        edges.add(new QosRouting.Edge(0, 1, 50, 0, 5, 1e-9, 3));
        edges.add(new QosRouting.Edge(1, 2, 50, 0, 5, 1e-9, 4));

        int sourceNode = 0;
        int destinationNode = 2;
        int requiredBandwidth = 40;
        int maxLatency = 20;
        double maxPacketLossProbability = 1e-8; // Combined loss is approximately 2e-9, which is within threshold.
        List<Integer> expected = Arrays.asList(0, 1, 2);
        List<Integer> result = QosRouting.findOptimalPath(numNodes, edges, sourceNode, destinationNode, requiredBandwidth, maxLatency, maxPacketLossProbability);
        assertEquals(expected, result);
    }
}