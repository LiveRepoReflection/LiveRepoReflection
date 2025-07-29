import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class QuantumNetworkTest {
    
    @Test
    void testBasicPath() {
        int n = 5;
        int[][] edges = {
            {0, 1, 10, 90}, // Using integers for fidelity (multiply by 0.01 for actual value)
            {0, 2, 15, 80},
            {1, 2, 5, 95},
            {1, 3, 12, 85},
            {2, 4, 8, 90},
            {3, 4, 7, 92}
        };
        int s = 0;
        int d = 4;
        int F = 65; // 0.65 * 100

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(23);
    }

    @Test
    void testSimplePath() {
        int n = 3;
        int[][] edges = {
            {0, 1, 5, 50},
            {1, 2, 7, 60}
        };
        int s = 0;
        int d = 2;
        int F = 30;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(12);
    }

    @Test
    void testNoValidPath() {
        int n = 3;
        int[][] edges = {
            {0, 1, 5, 50},
            {1, 2, 7, 60}
        };
        int s = 0;
        int d = 2;
        int F = 40;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(-1);
    }

    @Test
    void testDisconnectedGraph() {
        int n = 4;
        int[][] edges = {
            {0, 1, 5, 90},
            {2, 3, 7, 90}
        };
        int s = 0;
        int d = 3;
        int F = 50;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(-1);
    }

    @Test
    void testMultipleValidPaths() {
        int n = 4;
        int[][] edges = {
            {0, 1, 10, 90},
            {1, 3, 15, 90},
            {0, 2, 20, 95},
            {2, 3, 5, 95}
        };
        int s = 0;
        int d = 3;
        int F = 80;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(25);
    }

    @Test
    void testSingleNodePath() {
        int n = 1;
        int[][] edges = {};
        int s = 0;
        int d = 0;
        int F = 100;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(0);
    }

    @Test
    void testComplexNetwork() {
        int n = 6;
        int[][] edges = {
            {0, 1, 10, 95},
            {0, 2, 15, 90},
            {1, 2, 5, 95},
            {1, 3, 12, 85},
            {2, 3, 8, 90},
            {2, 4, 7, 92},
            {3, 4, 6, 93},
            {3, 5, 10, 88},
            {4, 5, 5, 95}
        };
        int s = 0;
        int d = 5;
        int F = 75;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(27);
    }

    @Test
    void testHighFidelityRequirement() {
        int n = 4;
        int[][] edges = {
            {0, 1, 5, 99},
            {1, 2, 5, 99},
            {2, 3, 5, 99}
        };
        int s = 0;
        int d = 3;
        int F = 95;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(15);
    }

    @Test
    void testParallelEdges() {
        int n = 3;
        int[][] edges = {
            {0, 1, 10, 90},
            {0, 1, 5, 80},
            {1, 2, 7, 95}
        };
        int s = 0;
        int d = 2;
        int F = 70;

        QuantumNetwork network = new QuantumNetwork(n, edges, s, d, F);
        assertThat(network.findMinCostPath()).isEqualTo(12);
    }
}