import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class NetworkLatencyCalculatorTest {

    // Assuming NetworkLatencyCalculator has a method:
    // public int minimumLatency(int n, int[][] partialConnectivity)
    // which returns the minimum overall communication latency or -1 if impossible.

    @Test
    public void testSampleCase() {
        int n = 3;
        int[][] partialConnectivity = {
            {0, -1, 2},
            {-1, 0, -1},
            {2, -1, 0}
        };
        // For missing edges, the minimum allowable assignment is 1.
        // Hence, one optimal completedConnectivity is:
        // [ [0, 1, 2],
        //   [1, 0, 1],
        //   [2, 1, 0] ]
        // Shortest paths:
        // 0-1: 1, 0-2: 2, 1-2: 1, overall latency = 1 + 2 + 1 = 4.
        int expected = 4;
        NetworkLatencyCalculator calculator = new NetworkLatencyCalculator();
        int actual = calculator.minimumLatency(n, partialConnectivity);
        assertEquals(expected, actual, "Sample case did not yield the expected overall latency.");
    }

    @Test
    public void testSingleNode() {
        int n = 1;
        int[][] partialConnectivity = {
            {0}
        };
        // Only one server, so overall latency = 0.
        int expected = 0;
        NetworkLatencyCalculator calculator = new NetworkLatencyCalculator();
        int actual = calculator.minimumLatency(n, partialConnectivity);
        assertEquals(expected, actual, "Single node graph should have 0 overall latency.");
    }

    @Test
    public void testCompleteMatrix() {
        int n = 4;
        int[][] partialConnectivity = {
            {0, 4, 5, 6},
            {4, 0, 7, 8},
            {5, 7, 0, 3},
            {6, 8, 3, 0}
        };
        // With all edges specified, the only valid assignment is to take these weights.
        // The shortest path distances are:
        // (0,1)=4, (0,2)=5, (0,3)=6, (1,2)=7, (1,3)=8, (2,3)=3.
        // Sum = 4+5+6+7+8+3 = 33.
        int expected = 33;
        NetworkLatencyCalculator calculator = new NetworkLatencyCalculator();
        int actual = calculator.minimumLatency(n, partialConnectivity);
        assertEquals(expected, actual, "Complete matrix case did not yield the expected overall latency.");
    }

    @Test
    public void testAllUnspecifiedEdges() {
        int n = 3;
        int[][] partialConnectivity = {
            {0, -1, -1},
            {-1, 0, -1},
            {-1, -1, 0}
        };
        // With all missing edges, the optimal filled graph assigns weight 1 to each edge.
        // Completed graph: all direct edge weights = 1.
        // Shortest path distances for pairs: (0,1)=1, (0,2)=1, (1,2)=1.
        // Sum = 1 + 1 + 1 = 3.
        int expected = 3;
        NetworkLatencyCalculator calculator = new NetworkLatencyCalculator();
        int actual = calculator.minimumLatency(n, partialConnectivity);
        assertEquals(expected, actual, "All unspecified edges case did not yield the expected overall latency.");
    }

    @Test
    public void testImpossibleCase() {
        int n = 3;
        int[][] partialConnectivity = {
            {0, 5, -1},
            {5, 0, 0},
            {-1, 0, 0}
        };
        // In this case, the input violates the requirement that for i != j, 
        // partialConnectivity[i][j] must be either -1 or at least 1.
        // Since a valid completedConnectivity cannot have a direct connection value of 0 for i != j,
        // the function should detect the inconsistency and return -1.
        int expected = -1;
        NetworkLatencyCalculator calculator = new NetworkLatencyCalculator();
        int actual = calculator.minimumLatency(n, partialConnectivity);
        assertEquals(expected, actual, "Inconsistent connectivity constraints should result in -1 (impossible).");
    }
}