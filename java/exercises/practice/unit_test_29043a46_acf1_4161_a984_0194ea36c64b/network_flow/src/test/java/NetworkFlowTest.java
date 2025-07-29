import org.junit.Test;
import org.junit.Assert;
import java.util.ArrayList;
import java.util.List;

public class NetworkFlowTest {

    // Helper method to create a list from given int arrays
    private List<int[]> createList(int[][] arr) {
        List<int[]> list = new ArrayList<>();
        for (int[] a : arr) {
            list.add(a);
        }
        return list;
    }

    // Test 1: Basic flow with a single direct link
    @Test
    public void testBasicFlow() {
        int N = 2;
        List<int[]> links = createList(new int[][] { {0, 1, 10} });
        int source = 0;
        int sink = 1;
        // For nodes with no specific demand, we set demand to 0.
        List<int[]> demands = createList(new int[][] { {0, 0}, {1, 0} });
        // Set supplies high enough for source and sink.
        List<int[]> supplies = createList(new int[][] { {0, 10}, {1, 10} });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(10, maxFlow);
    }

    // Test 2: Supply limitation restricts the flow through an intermediate node.
    @Test
    public void testSupplyLimitation() {
        int N = 4;
        List<int[]> links = createList(new int[][] {
            {0, 1, 15},
            {0, 2, 10},
            {1, 3, 10},
            {2, 3, 10},
            {1, 2, 5}
        });
        int source = 0;
        int sink = 3;
        List<int[]> demands = createList(new int[][] {
            {0, 0},
            {1, 0},
            {2, 0},
            {3, 15}
        });
        List<int[]> supplies = createList(new int[][] {
            {0, 20},
            {1, 10}, // limited supply at node 1
            {2, 10},
            {3, 100}
        });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(20, maxFlow);
    }

    // Test 3: No feasible flow exists to meet the demand.
    @Test
    public void testNoFeasible() {
        int N = 2;
        List<int[]> links = createList(new int[][] { {0, 1, 10} });
        int source = 0;
        int sink = 1;
        List<int[]> demands = createList(new int[][] { {0, 0}, {1, 15} });
        List<int[]> supplies = createList(new int[][] { {0, 10}, {1, 10} });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(-1, maxFlow);
    }

    // Test 4: Multiple edges between the same pair of nodes.
    @Test
    public void testMultiEdge() {
        int N = 2;
        List<int[]> links = createList(new int[][] {
            {0, 1, 5},
            {0, 1, 7}
        });
        int source = 0;
        int sink = 1;
        List<int[]> demands = createList(new int[][] { {0, 0}, {1, 0} });
        List<int[]> supplies = createList(new int[][] { {0, 20}, {1, 20} });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(12, maxFlow);
    }

    // Test 5: Graph with a cycle that should not affect maximum flow.
    @Test
    public void testCycle() {
        int N = 3;
        List<int[]> links = createList(new int[][] {
            {0, 1, 10},
            {1, 2, 10},
            {1, 0, 5}  // cycle edge back to source
        });
        int source = 0;
        int sink = 2;
        List<int[]> demands = createList(new int[][] { {0, 0}, {1, 0}, {2, 0} });
        List<int[]> supplies = createList(new int[][] { {0, 20}, {1, 20}, {2, 20} });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(10, maxFlow);
    }

    // Test 6: Disconnected graph where sink is unreachable.
    @Test
    public void testIsolatedSink() {
        int N = 3;
        List<int[]> links = createList(new int[][] {
            {0, 1, 5}
        });
        int source = 0;
        int sink = 2;
        List<int[]> demands = createList(new int[][] { {0, 0}, {1, 0}, {2, 0} });
        List<int[]> supplies = createList(new int[][] { {0, 10}, {1, 10}, {2, 10} });
        
        NetworkFlowOptimization solver = new NetworkFlowOptimization();
        int maxFlow = solver.maxFlow(N, links, source, sink, demands, supplies);
        Assert.assertEquals(0, maxFlow);
    }
}