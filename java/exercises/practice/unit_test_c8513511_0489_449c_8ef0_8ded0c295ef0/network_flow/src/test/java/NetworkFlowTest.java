import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class NetworkFlowTest {

    @Test
    public void testBasicExample() {
        int n = 4;
        int[][] edges = {
            {0, 1, 10},
            {0, 2, 10},
            {1, 2, 2},
            {1, 3, 10},
            {2, 3, 10}
        };
        int[] nodeCapacities = {Integer.MAX_VALUE, 5, 8, Integer.MAX_VALUE};
        int source = 0;
        int sink = 3;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(13, result);
    }

    @Test
    public void testNoEdges() {
        int n = 3;
        int[][] edges = new int[0][];
        int[] nodeCapacities = {Integer.MAX_VALUE, 10, Integer.MAX_VALUE};
        int source = 0;
        int sink = 2;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(0, result);
    }

    @Test
    public void testMultiplePaths() {
        int n = 6;
        int[][] edges = {
            {0, 1, 10},
            {0, 2, 10},
            {1, 3, 4},
            {1, 4, 8},
            {2, 4, 9},
            {2, 3, 5},
            {3, 5, 10},
            {4, 5, 10}
        };
        int[] nodeCapacities = {Integer.MAX_VALUE, 10, 10, 7, 8, Integer.MAX_VALUE};
        int source = 0;
        int sink = 5;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(15, result);
    }

    @Test
    public void testCycleGraph() {
        int n = 5;
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 5},
            {2, 3, 5},
            {3, 1, 3},
            {3, 4, 5}
        };
        int[] nodeCapacities = {Integer.MAX_VALUE, 5, 5, 5, Integer.MAX_VALUE};
        int source = 0;
        int sink = 4;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(5, result);
    }

    @Test
    public void testMultipleEdgesBetweenNodes() {
        int n = 3;
        int[][] edges = {
            {0, 1, 5},
            {0, 1, 7},
            {1, 2, 10}
        };
        int[] nodeCapacities = {Integer.MAX_VALUE, 12, Integer.MAX_VALUE};
        int source = 0;
        int sink = 2;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(10, result);
    }

    @Test
    public void testLargeCapacities() {
        int n = 4;
        int[][] edges = {
            {0, 1, 1000},
            {1, 2, 1000},
            {2, 3, 1000}
        };
        int[] nodeCapacities = {Integer.MAX_VALUE, 500, 800, Integer.MAX_VALUE};
        int source = 0;
        int sink = 3;
        NetworkFlow networkFlow = new NetworkFlow(n, edges, nodeCapacities, source, sink);
        int result = networkFlow.maxFlow();
        assertEquals(500, result);
    }
}