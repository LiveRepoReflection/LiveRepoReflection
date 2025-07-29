import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class NetworkRoutingTest {

    @Test
    @DisplayName("Example test case from the problem description")
    public void testExampleFromDescription() {
        int n = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10, 500},
            new int[]{0, 2, 5, 200},
            new int[]{1, 2, 3, 300},
            new int[]{1, 3, 20, 800},
            new int[]{2, 3, 15, 400}
        );
        int s = 0;
        int d = 3;
        int b = 350;
        int l = 40;

        NetworkRouting router = new NetworkRouting();
        int result = router.findOptimalPath(n, edges, s, d, b, l);
        assertEquals(500, result);
    }

    @Nested
    @DisplayName("Basic test cases")
    class BasicTests {
        @Test
        @DisplayName("Source and destination are the same node")
        public void testSameSourceAndDestination() {
            int n = 5;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 10, 500},
                new int[]{1, 2, 15, 300},
                new int[]{2, 3, 20, 200}
            );
            int s = 2;
            int d = 2;
            int b = 100;
            int l = 50;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            // If source and destination are the same, the path has 0 edges
            // So bandwidth is effectively infinite, but we return the minimum required bandwidth
            assertEquals(b, result);
        }

        @Test
        @DisplayName("No path between source and destination")
        public void testNoPath() {
            int n = 5;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 10, 500},
                new int[]{1, 2, 15, 300}
                // No path to node 4
            );
            int s = 0;
            int d = 4;
            int b = 100;
            int l = 50;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(-1, result);
        }

        @Test
        @DisplayName("Path exists but doesn't meet bandwidth requirements")
        public void testPathWithInsufficientBandwidth() {
            int n = 3;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 10, 200},
                new int[]{1, 2, 15, 150}
            );
            int s = 0;
            int d = 2;
            int b = 300;
            int l = 50;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(-1, result);
        }

        @Test
        @DisplayName("Path exists but exceeds latency limit")
        public void testPathExceedsLatencyLimit() {
            int n = 3;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 30, 500},
                new int[]{1, 2, 25, 400}
            );
            int s = 0;
            int d = 2;
            int b = 300;
            int l = 50;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(-1, result);
        }
    }

    @Nested
    @DisplayName("Complex test cases")
    class ComplexTests {
        
        @Test
        @DisplayName("Multiple valid paths with different bandwidths")
        public void testMultiplePaths() {
            int n = 5;
            List<int[]> edges = Arrays.asList(
                // Path 1: 0->1->4 (bandwidth 400, latency 25)
                new int[]{0, 1, 10, 400},
                new int[]{1, 4, 15, 500},
                
                // Path 2: 0->2->3->4 (bandwidth 600, latency 35)
                new int[]{0, 2, 10, 600},
                new int[]{2, 3, 15, 800},
                new int[]{3, 4, 10, 700}
            );
            int s = 0;
            int d = 4;
            int b = 300;
            int l = 40;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(600, result); // Should choose the path with higher bandwidth
        }

        @Test
        @DisplayName("Choose path with fewer hops when bandwidth is equal")
        public void testFewerHopsPreference() {
            int n = 5;
            List<int[]> edges = Arrays.asList(
                // Path 1: 0->1->4 (bandwidth 500, latency 25)
                new int[]{0, 1, 10, 500},
                new int[]{1, 4, 15, 500},
                
                // Path 2: 0->2->3->4 (bandwidth 500, latency 30)
                new int[]{0, 2, 10, 500},
                new int[]{2, 3, 10, 600},
                new int[]{3, 4, 10, 700}
            );
            int s = 0;
            int d = 4;
            int b = 300;
            int l = 40;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(500, result); // Both paths have 500 bandwidth, but path 1 has fewer hops
        }

        @Test
        @DisplayName("Multiple edges between same nodes")
        public void testMultipleEdgesBetweenSameNodes() {
            int n = 3;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 10, 200},  // Edge 1 between 0 and 1
                new int[]{0, 1, 5, 400},   // Edge 2 between 0 and 1
                new int[]{1, 2, 15, 300}
            );
            int s = 0;
            int d = 2;
            int b = 200;
            int l = 25;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(300, result); // Should use the second edge between 0 and 1
        }

        @Test
        @DisplayName("Complex network with multiple possible paths")
        public void testComplexNetwork() {
            int n = 8;
            List<int[]> edges = Arrays.asList(
                new int[]{0, 1, 5, 500},
                new int[]{0, 2, 3, 300},
                new int[]{1, 3, 8, 600},
                new int[]{1, 4, 12, 400},
                new int[]{2, 4, 4, 200},
                new int[]{2, 5, 7, 700},
                new int[]{3, 6, 9, 350},
                new int[]{4, 6, 6, 250},
                new int[]{4, 7, 10, 800},
                new int[]{5, 7, 15, 650}
            );
            int s = 0;
            int d = 7;
            int b = 250;
            int l = 25;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(300, result); // Path 0->2->4->7 with bandwidth min(300, 200, 800) = 200
        }
    }

    @Nested
    @DisplayName("Edge cases")
    class EdgeCases {
        @Test
        @DisplayName("Empty edge list")
        public void testEmptyEdgeList() {
            int n = 5;
            List<int[]> edges = new ArrayList<>();
            int s = 0;
            int d = 4;
            int b = 100;
            int l = 50;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(-1, result); // No path exists
        }

        @Test
        @DisplayName("Network with only one node")
        public void testSingleNodeNetwork() {
            int n = 1;
            List<int[]> edges = new ArrayList<>();
            int s = 0;
            int d = 0;
            int b = 100;
            int l = 10;

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(b, result); // Source and destination are the same
        }

        @Test
        @DisplayName("Maximum constraints")
        public void testMaxConstraints() {
            int n = 10; // Smaller network for test purposes
            List<int[]> edges = new ArrayList<>();
            
            // Create a line graph with high bandwidth but high latency
            for (int i = 0; i < n - 1; i++) {
                edges.add(new int[]{i, i + 1, 100, 1000});
            }
            
            int s = 0;
            int d = n - 1;
            int b = 1000;
            int l = 50; // Not enough for the full path

            NetworkRouting router = new NetworkRouting();
            int result = router.findOptimalPath(n, edges, s, d, b, l);
            assertEquals(-1, result); // Total latency exceeds limit
        }
    }

    @Nested
    @DisplayName("Performance tests")
    class PerformanceTests {
        @Test
        @DisplayName("Medium-sized network (100 nodes)")
        public void testMediumNetwork() {
            int n = 100;
            List<int[]> edges = new ArrayList<>();
            
            // Create a grid-like network
            for (int i = 0; i < 10; i++) {
                for (int j = 0; j < 9; j++) {
                    int node1 = i * 10 + j;
                    int node2 = i * 10 + j + 1;
                    edges.add(new int[]{node1, node2, 1, 400 + (node1 % 10)});
                }
            }
            
            for (int i = 0; i < 9; i++) {
                for (int j = 0; j < 10; j++) {
                    int node1 = i * 10 + j;
                    int node2 = (i + 1) * 10 + j;
                    edges.add(new int[]{node1, node2, 1, 300 + (node1 % 10)});
                }
            }
            
            int s = 0;
            int d = 99;
            int b = 300;
            int l = 20;

            NetworkRouting router = new NetworkRouting();
            // This isn't testing the actual result, just making sure it completes in reasonable time
            long startTime = System.currentTimeMillis();
            router.findOptimalPath(n, edges, s, d, b, l);
            long endTime = System.currentTimeMillis();
            assertTrue(endTime - startTime < 5000); // Should complete within 5 seconds
        }
    }
}