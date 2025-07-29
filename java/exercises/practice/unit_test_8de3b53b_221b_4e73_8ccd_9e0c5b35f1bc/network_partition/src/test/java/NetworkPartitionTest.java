import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import java.util.ArrayList;
import java.util.List;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class NetworkPartitionTest {

    private NetworkPartition solver;

    @BeforeEach
    public void setUp() {
        solver = new NetworkPartition();
    }

    @Test
    public void testChainGraph_SplitsCorrectly_Level2() {
        int n = 5;
        int k = 2;
        // Chain graph: 0-1, 1-2, 2-3, 3-4
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1});
        edges.add(new int[]{1, 2});
        edges.add(new int[]{2, 3});
        edges.add(new int[]{3, 4});
        int expected = 1;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }

    @Test
    public void testChainGraph_SplitsCorrectly_Level3() {
        int n = 5;
        int k = 3;
        // Chain graph: 0-1, 1-2, 2-3, 3-4
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1});
        edges.add(new int[]{1, 2});
        edges.add(new int[]{2, 3});
        edges.add(new int[]{3, 4});
        int expected = 2;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }

    @Test
    public void testImpossiblePartition() {
        int n = 3;
        int k = 4;
        // Chain graph: 0-1, 1-2
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1});
        edges.add(new int[]{1, 2});
        int expected = -1;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }
    
    @Test
    public void testAlreadyDisconnected() {
        int n = 6;
        int k = 2;
        // Graph with two disconnected components:
        // Component1: 0-1-2; Component2: 3-4-5
        List<int[]> edges = new ArrayList<>();
        edges.add(new int[]{0, 1});
        edges.add(new int[]{1, 2});
        edges.add(new int[]{3, 4});
        edges.add(new int[]{4, 5});
        int expected = 0;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }

    @Test
    public void testSingleNode() {
        int n = 1;
        int k = 1;
        // Single node graph.
        List<int[]> edges = new ArrayList<>();
        int expected = 0;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }

    @Test
    public void testCompleteGraphImpossible() {
        int n = 4;
        int k = 2;
        // Complete graph: every node is connected to every other node.
        List<int[]> edges = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                edges.add(new int[]{i, j});
            }
        }
        int expected = -1;
        assertEquals(expected, solver.minNodesToRemove(n, k, edges));
    }
}