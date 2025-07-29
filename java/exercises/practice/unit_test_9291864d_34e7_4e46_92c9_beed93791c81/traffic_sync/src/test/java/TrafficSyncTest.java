import org.junit.Test;
import static org.junit.Assert.*;

public class TrafficSyncTest {

    @Test
    public void testMinimalGraph() {
        int N = 2;
        int[][] edges = { {0, 1, 10}, {1, 0, 10} };
        int[] cycleDuration = {30, 30};
        int[][] colorTimings = { {10, 10, 10}, {10, 10, 10} };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets array should not be null", offsets);
        assertEquals("Offsets array length should match number of intersections", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset at index " + i + " should be in range [0, cycleDuration)",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }

    @Test
    public void testCycleGraph() {
        int N = 3;
        int[][] edges = {
            {0, 1, 15},
            {1, 2, 20},
            {2, 0, 15},
            {0, 2, 40}
        };
        int[] cycleDuration = {40, 50, 60};
        int[][] colorTimings = {
            {15, 10, 15}, // Total = 40
            {20, 10, 20}, // Total = 50
            {25, 15, 20}  // Total = 60
        };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets must not be null", offsets);
        assertEquals("Offsets array length should be N", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset at node " + i + " must be within [0, cycleDuration)",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }

    @Test
    public void testWaitingTimes() {
        int N = 4;
        int[][] edges = {
            {0, 1, 10},
            {1, 2, 20},
            {2, 3, 15},
            {3, 0, 25},
            {0, 2, 35},
            {1, 3, 30}
        };
        int[] cycleDuration = {50, 50, 50, 50};
        int[][] colorTimings = {
            {20, 10, 20},
            {15, 15, 20},
            {10, 20, 20},
            {25, 5, 20}
        };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets array should not be null", offsets);
        assertEquals("There should be N offsets", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset at index " + i + " is out of the valid range",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }

    @Test
    public void testDenseGraph() {
        int N = 5;
        int totalEdges = N * (N - 1);
        int[][] edges = new int[totalEdges][3];
        int idx = 0;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (i != j) {
                    edges[idx][0] = i;
                    edges[idx][1] = j;
                    edges[idx][2] = 10;
                    idx++;
                }
            }
        }
        int[] cycleDuration = {60, 60, 60, 60, 60};
        int[][] colorTimings = {
            {20, 20, 20},
            {15, 15, 30},
            {10, 20, 30},
            {25, 5, 30},
            {20, 10, 30}
        };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets must be produced", offsets);
        assertEquals("Offset array length should equal number of intersections", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset for intersection " + i + " should be within valid range",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }

    @Test
    public void testZeroGreenTime() {
        int N = 3;
        int[][] edges = {
            {0, 1, 10},
            {1, 2, 10},
            {2, 0, 10}
        };
        int[] cycleDuration = {40, 40, 40};
        int[][] colorTimings = {
            {15, 10, 15},
            {20, 20, 0},
            {10, 15, 15}
        };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets array should not be null", offsets);
        assertEquals("There must be an offset for each intersection", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset at node " + i + " must be in range [0, cycleDuration)",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }

    @Test
    public void testVaryingTravelTimes() {
        int N = 6;
        int[][] edges = {
            {0, 1, 5},
            {1, 2, 15},
            {2, 3, 20},
            {3, 4, 25},
            {4, 5, 10},
            {5, 0, 30},
            {0, 3, 35},
            {1, 4, 40},
            {2, 5, 45}
        };
        int[] cycleDuration = {70, 70, 70, 70, 70, 70};
        int[][] colorTimings = {
            {25, 15, 30},
            {20, 20, 30},
            {15, 25, 30},
            {30, 10, 30},
            {20, 20, 30},
            {25, 15, 30}
        };

        int[] offsets = TrafficSync.optimizeOffsets(N, edges, cycleDuration, colorTimings);
        assertNotNull("Offsets should be computed", offsets);
        assertEquals("Returned offset array must have length N", N, offsets.length);
        for (int i = 0; i < N; i++) {
            assertTrue("Offset for intersection " + i + " must be within [0, cycleDuration)",
                    offsets[i] >= 0 && offsets[i] < cycleDuration[i]);
        }
    }
}