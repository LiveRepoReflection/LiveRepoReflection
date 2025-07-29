package network_flow;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class NetworkFlowTest {

    @Test
    public void testExampleFromDescription() {
        int n = 6;
        int[][] edges = {
            {0, 1, 16},
            {0, 2, 13},
            {1, 2, 10},
            {1, 3, 12},
            {2, 1, 4},
            {2, 4, 14},
            {3, 2, 9},
            {3, 5, 20},
            {4, 3, 7},
            {4, 5, 4}
        };
        int[] sources = {0};
        int[] sinks = {5};
        int[] nodeBandwidths = {50, 50, 50, 50, 50, 50};
        
        int maxFlow = NetworkFlow.maxFlow(n, edges, sources, sinks, nodeBandwidths);
        assertEquals(23, maxFlow);
    }

    @Test
    public void testMultipleSources() {
        int n = 4;
        int[][] edges = {
            {0, 2, 5},
            {1, 2, 10},
            {2, 3, 15}
        };
        int[] sources = {0, 1};
        int[] sinks = {3};
        int[] nodeBandwidths = {20, 20, 20, 20};
        
        int maxFlow = NetworkFlow.maxFlow(n, edges, sources, sinks, nodeBandwidths);
        assertEquals(15, maxFlow);
    }

    @Test
    public void testNodeBandwidthLimit() {
        int n = 3;
        int[][] edges = {
            {0, 1, 100},
            {1, 2, 100}
        };
        int[] sources = {0};
        int[] sinks = {2};
        int[] nodeBandwidths = {100, 50, 100};
        
        int maxFlow = NetworkFlow.maxFlow(n, edges, sources, sinks, nodeBandwidths);
        assertEquals(50, maxFlow);
    }

    @Test
    public void testNoEdgeCase() {
        int n = 3;
        int[][] edges = {};
        int[] sources = {0};
        int[] sinks = {2};
        int[] nodeBandwidths = {100, 100, 100};
        
        int maxFlow = NetworkFlow.maxFlow(n, edges, sources, sinks, nodeBandwidths);
        assertEquals(0, maxFlow);
    }

    @Test
    public void testCyclicGraph() {
        int n = 5;
        int[][] edges = {
            {0, 1, 10},
            {1, 2, 5},
            {2, 3, 10},
            {3, 1, 15},
            {3, 4, 10}
        };
        int[] sources = {0};
        int[] sinks = {4};
        int[] nodeBandwidths = {20, 20, 20, 20, 20};
        
        int maxFlow = NetworkFlow.maxFlow(n, edges, sources, sinks, nodeBandwidths);
        assertEquals(5, maxFlow);
    }
}