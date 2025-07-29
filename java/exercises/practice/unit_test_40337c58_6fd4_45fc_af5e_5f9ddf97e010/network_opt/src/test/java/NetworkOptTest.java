package network_opt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class NetworkOptTest {

    @Test
    public void testSmallGraph() {
        int n = 4;
        int[][] edges = new int[][] {
            {0, 1, 1},
            {0, 2, 5},
            {1, 2, 2},
            {1, 3, 1},
            {2, 3, 3}
        };
        int k = 4;
        double result = NetworkOptSolver.minAveragePath(n, edges, k);
        assertEquals(2.0, result, 1e-5);
    }

    @Test
    public void testDisconnectedGraph() {
        int n = 3;
        int[][] edges = new int[][] {
            {0, 1, 2}
        };
        int k = 1;
        double result = NetworkOptSolver.minAveragePath(n, edges, k);
        assertEquals(Double.MAX_VALUE, result, 1e-5);
    }

    @Test
    public void testTwoNodesGraph() {
        int n = 2;
        int[][] edges = new int[][] {
            {0, 1, 10}
        };
        int k = 1;
        double result = NetworkOptSolver.minAveragePath(n, edges, k);
        assertEquals(10.0, result, 1e-5);
    }

    @Test
    public void testTriangleGraph() {
        int n = 3;
        int[][] edges = new int[][] {
            {0, 1, 2},
            {1, 2, 3},
            {0, 2, 1}
        };
        int k = 2;
        double result = NetworkOptSolver.minAveragePath(n, edges, k);
        assertEquals(2.0, result, 1e-5);
    }

    @Test
    public void testLargerGraph() {
        int n = 5;
        int[][] edges = new int[][] {
            {0, 1, 3},
            {1, 2, 1},
            {0, 2, 4},
            {2, 3, 2},
            {1, 3, 7},
            {3, 4, 1},
            {2, 4, 8}
        };
        int k = 5;
        // Expected spanning tree: (0,1,3), (1,2,1), (2,3,2), (3,4,1)
        // Pairwise shortest paths:
        // 0-1: 3, 0-2: 3+1=4, 0-3: 3+1+2=6, 0-4: 3+1+2+1=7,
        // 1-2: 1, 1-3: 1+2=3, 1-4: 1+2+1=4,
        // 2-3: 2, 2-4: 2+1=3, 3-4: 1.
        // Sum = 34, Total pairs = 10, Average = 3.4
        double result = NetworkOptSolver.minAveragePath(n, edges, k);
        assertEquals(3.4, result, 1e-5);
    }
}