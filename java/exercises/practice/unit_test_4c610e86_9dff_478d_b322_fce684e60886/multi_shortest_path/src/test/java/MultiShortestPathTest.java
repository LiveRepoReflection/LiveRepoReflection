import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import java.util.List;
import java.util.ArrayList;

public class MultiShortestPathTest {

    @Test
    public void testBasicGraph() {
        // Graph:
        // 0 -> 1 (cost 5), 0 -> 2 (cost 3)
        // 1 -> 3 (cost 6)
        // 2 -> 3 (cost 2)
        // 3 -> 4 (cost 4)
        // 4 -> 1 (cost 1)
        int n = 5;
        List<MultiShortestPath.Edge> edges = new ArrayList<>();
        edges.add(new MultiShortestPath.Edge(0, 1, 5));
        edges.add(new MultiShortestPath.Edge(0, 2, 3));
        edges.add(new MultiShortestPath.Edge(1, 3, 6));
        edges.add(new MultiShortestPath.Edge(2, 3, 2));
        edges.add(new MultiShortestPath.Edge(3, 4, 4));
        edges.add(new MultiShortestPath.Edge(4, 1, 1));

        // Sources: 0 and 4. For source nodes, cost should be 0.
        List<Integer> sources = new ArrayList<>();
        sources.add(0);
        sources.add(4);

        // Expected result:
        // City 0: cost 0 (source)
        // City 1: minimum cost from source 4 -> 1 is 1 (via edge (4,1,1))
        // City 2: reachable from 0 with cost 3
        // City 3: reachable from 0 via 0->2->3 = 3+2 = 5 OR from 4 through 4->1->3 = 1+6 = 7, so 5.
        // City 4: cost 0 (source)
        int[] expected = {0, 1, 3, 5, 0};

        int[] result = MultiShortestPath.findMinCosts(n, edges, sources);
        assertArrayEquals(expected, result);
    }

    @Test
    public void testDisconnectedGraph() {
        // Graph:
        // 0 -> 1 (cost 2), 1 -> 2 (cost 3)
        // Node 3 is disconnected.
        int n = 4;
        List<MultiShortestPath.Edge> edges = new ArrayList<>();
        edges.add(new MultiShortestPath.Edge(0, 1, 2));
        edges.add(new MultiShortestPath.Edge(1, 2, 3));

        List<Integer> sources = new ArrayList<>();
        sources.add(0);

        // Expected:
        // City 0: 0 (source)
        // City 1: 2
        // City 2: 5
        // City 3: -1 (unreachable)
        int[] expected = {0, 2, 5, -1};

        int[] result = MultiShortestPath.findMinCosts(n, edges, sources);
        assertArrayEquals(expected, result);
    }

    @Test
    public void testCycleGraph() {
        // Graph with cycle:
        // 0 -> 1 (cost 4), 1 -> 2 (cost 5), 2 -> 0 (cost 2)
        int n = 3;
        List<MultiShortestPath.Edge> edges = new ArrayList<>();
        edges.add(new MultiShortestPath.Edge(0, 1, 4));
        edges.add(new MultiShortestPath.Edge(1, 2, 5));
        edges.add(new MultiShortestPath.Edge(2, 0, 2));

        List<Integer> sources = new ArrayList<>();
        sources.add(1);

        // Expected:
        // City 0: From source 1: 1->2->0 = 5 + 2 = 7.
        // City 1: 0 (source)
        // City 2: 5 (direct edge from 1)
        int[] expected = {7, 0, 5};

        int[] result = MultiShortestPath.findMinCosts(n, edges, sources);
        assertArrayEquals(expected, result);
    }

    @Test
    public void testMultipleEdges() {
        // Graph with multiple edges between same nodes:
        // 0 -> 1 with cost 10 and also 0 -> 1 with cost 3
        // 1 -> 2 (cost 7)
        int n = 3;
        List<MultiShortestPath.Edge> edges = new ArrayList<>();
        edges.add(new MultiShortestPath.Edge(0, 1, 10));
        edges.add(new MultiShortestPath.Edge(0, 1, 3));
        edges.add(new MultiShortestPath.Edge(1, 2, 7));

        List<Integer> sources = new ArrayList<>();
        sources.add(0);

        // Expected:
        // City 0: 0 (source)
        // City 1: 3 (cheaper edge)
        // City 2: 3 + 7 = 10
        int[] expected = {0, 3, 10};

        int[] result = MultiShortestPath.findMinCosts(n, edges, sources);
        assertArrayEquals(expected, result);
    }

    @Test
    public void testEmptySources() {
        // When there are no sources, all nodes should be marked as unreachable (-1)
        int n = 3;
        List<MultiShortestPath.Edge> edges = new ArrayList<>();
        edges.add(new MultiShortestPath.Edge(0, 1, 5));
        edges.add(new MultiShortestPath.Edge(1, 2, 5));

        List<Integer> sources = new ArrayList<>();
        // No sources added

        int[] expected = {-1, -1, -1};
        int[] result = MultiShortestPath.findMinCosts(n, edges, sources);
        assertArrayEquals(expected, result);
    }
}