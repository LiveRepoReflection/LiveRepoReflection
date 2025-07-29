import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;
import static org.assertj.core.api.Assertions.assertThat;

public class OptimalPathsTest {

    @Test
    public void testExampleCase() {
        int n = 6;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 2, 10},
            new int[]{0, 2, 4, 5},
            new int[]{1, 3, 5, 15},
            new int[]{2, 3, 1, 8},
            new int[]{3, 4, 3, 20},
            new int[]{4, 5, 2, 7}
        );
        List<Integer> sources = Arrays.asList(0, 2);
        int target = 5;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(6);
    }

    @Test
    public void testNoPathExists() {
        int n = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1, 5},
            new int[]{1, 2, 1, 5}
        );
        List<Integer> sources = Arrays.asList(0);
        int target = 3;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(-1);
    }

    @Test
    public void testCapacityConstraint() {
        int n = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1, 0}, // Zero capacity - cannot be used
            new int[]{0, 2, 2, 10},
            new int[]{2, 3, 3, 10}
        );
        List<Integer> sources = Arrays.asList(0);
        int target = 3;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(5); // Path 0->2->3 with distance 2+3=5
    }

    @Test
    public void testMultipleSourceNodes() {
        int n = 6;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10, 10}, 
            new int[]{0, 2, 10, 10},
            new int[]{1, 3, 10, 10},
            new int[]{2, 3, 10, 10},
            new int[]{3, 5, 10, 10},
            new int[]{4, 5, 1, 10}
        );
        List<Integer> sources = Arrays.asList(0, 4);
        int target = 5;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(1); // Path from source 4 to target 5
    }

    @Test
    public void testCyclicGraph() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1, 10}, 
            new int[]{1, 2, 1, 10},
            new int[]{2, 3, 1, 10},
            new int[]{3, 1, 1, 10}, // Creates a cycle
            new int[]{3, 4, 1, 10}
        );
        List<Integer> sources = Arrays.asList(0);
        int target = 4;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(4); // Path 0->1->2->3->4
    }

    @Test
    public void testTargetIsSource() {
        int n = 3;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 5, 10},
            new int[]{1, 2, 5, 10}
        );
        List<Integer> sources = Arrays.asList(0, 2);
        int target = 2;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(0); // Target is already a source
    }

    @Test
    public void testLargeGraph() {
        int n = 1000;
        List<int[]> edges = new ArrayList<>();
        
        // Create a linear path from 0 to 999
        for (int i = 0; i < n - 1; i++) {
            edges.add(new int[]{i, i + 1, 1, 10});
        }
        
        List<Integer> sources = Arrays.asList(0);
        int target = 999;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(999); // Linear path of length 999
    }

    @Test
    public void testAlternativePaths() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 5, 10},
            new int[]{0, 2, 2, 10},
            new int[]{1, 3, 1, 10},
            new int[]{2, 3, 4, 10},
            new int[]{3, 4, 3, 10}
        );
        List<Integer> sources = Arrays.asList(0);
        int target = 4;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(9); // Path 0->1->3->4 = 5+1+3 = 9
    }

    @Test
    public void testZeroCapacityEdges() {
        int n = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1, 0}, // Zero capacity
            new int[]{0, 2, 2, 0}, // Zero capacity
            new int[]{0, 3, 3, 10} // Only usable path
        );
        List<Integer> sources = Arrays.asList(0);
        int target = 3;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(3); // Only path 0->3
    }

    @Test
    public void testSingleNodeGraph() {
        int n = 1;
        List<int[]> edges = new ArrayList<>();
        List<Integer> sources = Arrays.asList(0);
        int target = 0;

        OptimalPaths solver = new OptimalPaths();
        int result = solver.findShortestPath(n, edges, sources, target);

        assertThat(result).isEqualTo(0); // Source is target
    }
}