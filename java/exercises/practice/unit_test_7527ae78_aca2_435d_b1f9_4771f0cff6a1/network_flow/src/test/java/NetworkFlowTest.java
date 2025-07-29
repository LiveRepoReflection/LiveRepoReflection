import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class NetworkFlowTest {

    @Test
    public void testEmptyGraph() {
        int n = 2;
        List<int[]> edges = new ArrayList<>();
        int source = 0;
        List<Integer> destinations = Arrays.asList(1);
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(0, result, "Empty graph should result in zero flow");
    }

    @Test
    public void testNoPathExists() {
        int n = 3;
        List<int[]> edges = new ArrayList<>();
        // Only one edge that does not lead to destination 2.
        edges.add(new int[]{0, 1, 10});
        int source = 0;
        List<Integer> destinations = Arrays.asList(2);
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(0, result, "No path exists so flow should be zero");
    }

    @Test
    public void testSingleEdge() {
        int n = 2;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        int source = 0;
        List<Integer> destinations = Arrays.asList(1);
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(10, result, "Single edge capacity should be the max flow");
    }

    @Test
    public void testMultiplePaths() {
        int n = 4;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        edges.add(new int[]{0, 2, 5});
        edges.add(new int[]{1, 3, 4});
        edges.add(new int[]{2, 3, 10});
        int source = 0;
        List<Integer> destinations = Arrays.asList(3);
        // Expected flow: route via 0->1->3 gives 4, and 0->2->3 gives 5, total = 9.
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(9, result, "Maximum flow should be 9 when combining two distinct paths");
    }

    @Test
    public void testMultipleDestinations() {
        int n = 5;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        edges.add(new int[]{0, 2, 5});
        edges.add(new int[]{1, 3, 4});
        edges.add(new int[]{2, 3, 6});
        edges.add(new int[]{1, 4, 5});
        edges.add(new int[]{2, 4, 4});
        int source = 0;
        // Destinations are nodes 3 and 4.
        List<Integer> destinations = Arrays.asList(3, 4);
        // Expected maximum flow breakdown:
        // From node 0, two branches: 0->1 (10 capacity) and 0->2 (5 capacity).
        // Branch 1: from 1 to destinations, possible split: up to 4 to node 3 and up to 5 to node 4.
        // Branch 2: from 2 to destinations, split between path 2->3 (6 cap, limited by 5 available from 0->2) and 2->4 (4 cap).
        // An optimal distribution can push a total flow of 14.
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(14, result, "Total max flow to multiple destinations should be 14");
    }

    @Test
    public void testCycleInGraph() {
        int n = 4;
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1, 10});
        edges.add(new int[]{1, 2, 5});
        edges.add(new int[]{2, 1, 3});
        edges.add(new int[]{2, 3, 10});
        int source = 0;
        List<Integer> destinations = Arrays.asList(3);
        // The cycle between nodes 1 and 2 should not inflate the flow.
        // The bottleneck is 1->2 with capacity 5, so max flow is 5.
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(5, result, "Cycle in graph should not allow flow to exceed bottleneck capacity");
    }

    @Test
    public void testMultipleEdgesBetweenNodes() {
        int n = 3;
        List<int[]> edges = new ArrayList<>();
        // Two edges from 0 to 1.
        edges.add(new int[]{0, 1, 5});
        edges.add(new int[]{0, 1, 7});
        // Single edge from 1 to 2.
        edges.add(new int[]{1, 2, 10});
        int source = 0;
        List<Integer> destinations = Arrays.asList(2);
        // Total capacity from 0 to 1 is 12, but edge 1->2 limits flow to 10.
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(10, result, "Multiple edges should aggregate capacity, but downstream limit applies");
    }

    @Test
    public void testSourceIsDestination() {
        int n = 1;
        List<int[]> edges = new ArrayList<>();
        int source = 0;
        // When the source is also the only destination, no transfer is needed.
        List<Integer> destinations = Arrays.asList(0);
        int result = NetworkFlow.maxFlow(n, edges, source, destinations);
        assertEquals(0, result, "Source equal to destination should yield zero flow");
    }
}