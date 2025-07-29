import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

public class ParallelPathsTest {
    
    private ParallelPaths solver;
    
    @BeforeEach
    public void setUp() {
        solver = new ParallelPaths();
    }
    
    @Test
    @DisplayName("Test shortest path in a small graph with a single thread")
    public void testSmallGraphSingleThread() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10},
            new int[]{0, 2, 5},
            new int[]{1, 3, 1},
            new int[]{2, 1, 3},
            new int[]{2, 3, 8},
            new int[]{2, 4, 2},
            new int[]{3, 4, 4}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(1, 3, 4);
        int numThreads = 1;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(8, 9, 7), result);
    }
    
    @Test
    @DisplayName("Test shortest path in a small graph with multiple threads")
    public void testSmallGraphMultipleThreads() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10},
            new int[]{0, 2, 5},
            new int[]{1, 3, 1},
            new int[]{2, 1, 3},
            new int[]{2, 3, 8},
            new int[]{2, 4, 2},
            new int[]{3, 4, 4}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(1, 3, 4);
        int numThreads = 3;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(8, 9, 7), result);
    }
    
    @Test
    @DisplayName("Test with unreachable nodes")
    public void testUnreachableNodes() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10},
            new int[]{1, 2, 5},
            new int[]{2, 3, 3}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(1, 3, 4);
        int numThreads = 2;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(10, 18, -1), result);
    }
    
    @Test
    @DisplayName("Test with duplicate destinations")
    public void testDuplicateDestinations() {
        int n = 4;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1},
            new int[]{1, 2, 2},
            new int[]{2, 3, 3}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(2, 3, 2, 3);
        int numThreads = 2;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(3, 6, 3, 6), result);
    }
    
    @Test
    @DisplayName("Test with a large graph")
    public void testLargeGraph() {
        int n = 1000;
        List<int[]> edges = new ArrayList<>();
        Random random = new Random(42); // Fixed seed for reproducibility
        
        for (int i = 0; i < n-1; i++) {
            edges.add(new int[]{i, i+1, random.nextInt(10) + 1});
        }
        
        // Add some random edges for complexity
        for (int i = 0; i < 2000; i++) {
            int u = random.nextInt(n);
            int v = random.nextInt(n);
            if (u != v) {
                edges.add(new int[]{u, v, random.nextInt(100) + 1});
            }
        }
        
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(100, 500, 999);
        
        List<Integer> singleThreadResult = solver.findShortestPaths(n, edges, sourceNode, destinations, 1);
        List<Integer> multiThreadResult = solver.findShortestPaths(n, edges, sourceNode, destinations, 4);
        
        assertEquals(singleThreadResult, multiThreadResult);
    }
    
    @Test
    @DisplayName("Test with a graph containing cycles")
    public void testGraphWithCycles() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 1},
            new int[]{1, 2, 2},
            new int[]{2, 0, 3},
            new int[]{2, 3, 4},
            new int[]{3, 4, 5},
            new int[]{4, 2, 6}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(3, 4);
        int numThreads = 2;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(7, 12), result);
    }
    
    @Test
    @DisplayName("Test with source node as destination")
    public void testSourceAsDestination() {
        int n = 5;
        List<int[]> edges = Arrays.asList(
            new int[]{0, 1, 10},
            new int[]{1, 2, 5}
        );
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(0, 1, 2);
        int numThreads = 2;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        assertEquals(Arrays.asList(0, 10, 15), result);
    }
    
    @Test
    @DisplayName("Test with different thread counts")
    public void testDifferentThreadCounts() {
        int n = 100;
        List<int[]> edges = new ArrayList<>();
        Random random = new Random(123);
        
        for (int i = 0; i < n-1; i++) {
            edges.add(new int[]{i, i+1, random.nextInt(10) + 1});
        }
        
        // Add some random edges for complexity
        for (int i = 0; i < 200; i++) {
            int u = random.nextInt(n);
            int v = random.nextInt(n);
            if (u != v) {
                edges.add(new int[]{u, v, random.nextInt(50) + 1});
            }
        }
        
        int sourceNode = 0;
        List<Integer> destinations = new ArrayList<>();
        for (int i = 0; i < 20; i++) {
            destinations.add(random.nextInt(n));
        }
        
        List<Integer> resultWithOneThread = solver.findShortestPaths(n, edges, sourceNode, destinations, 1);
        List<Integer> resultWithTwoThreads = solver.findShortestPaths(n, edges, sourceNode, destinations, 2);
        List<Integer> resultWithFourThreads = solver.findShortestPaths(n, edges, sourceNode, destinations, 4);
        
        assertEquals(resultWithOneThread, resultWithTwoThreads);
        assertEquals(resultWithOneThread, resultWithFourThreads);
    }
    
    @Test
    @DisplayName("Test with dense graph")
    public void testDenseGraph() {
        int n = 50;
        List<int[]> edges = new ArrayList<>();
        
        // Create a complete graph
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    edges.add(new int[]{i, j, i + j % 20 + 1});
                }
            }
        }
        
        int sourceNode = 0;
        List<Integer> destinations = Arrays.asList(10, 20, 30, 40, 49);
        int numThreads = 3;
        
        List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
        
        // Verify that all destinations are reachable
        assertFalse(result.contains(-1));
    }
    
    @Test
    @DisplayName("Test parallel performance improvement")
    public void testParallelPerformance() {
        int n = 10000;
        List<int[]> edges = new ArrayList<>();
        Random random = new Random(42);
        
        // Create a connected graph
        for (int i = 0; i < n-1; i++) {
            edges.add(new int[]{i, i+1, random.nextInt(10) + 1});
        }
        
        // Add random edges
        for (int i = 0; i < 50000; i++) {
            int u = random.nextInt(n);
            int v = random.nextInt(n);
            if (u != v) {
                edges.add(new int[]{u, v, random.nextInt(1000) + 1});
            }
        }
        
        int sourceNode = 0;
        List<Integer> destinations = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            destinations.add(random.nextInt(n));
        }
        
        // Measure sequential time
        long startSeq = System.currentTimeMillis();
        List<Integer> seqResult = solver.findShortestPaths(n, edges, sourceNode, destinations, 1);
        long endSeq = System.currentTimeMillis();
        long sequentialTime = endSeq - startSeq;
        
        // Measure parallel time (using number of available processors)
        int availableProcessors = Runtime.getRuntime().availableProcessors();
        long startPar = System.currentTimeMillis();
        List<Integer> parResult = solver.findShortestPaths(n, edges, sourceNode, destinations, availableProcessors);
        long endPar = System.currentTimeMillis();
        long parallelTime = endPar - startPar;
        
        // Check correctness
        assertEquals(seqResult, parResult);
        
        // We don't want the test to fail on CI systems where the performance might vary,
        // so we'll just print out the times. In a real-world scenario, we might assert
        // that the parallel version is faster by some factor.
        System.out.println("Sequential time: " + sequentialTime + "ms");
        System.out.println("Parallel time (" + availableProcessors + " threads): " + parallelTime + "ms");
    }
    
    @Test
    @DisplayName("Test edge cases")
    public void testEdgeCases() {
        // Single node graph
        {
            int n = 1;
            List<int[]> edges = new ArrayList<>();
            int sourceNode = 0;
            List<Integer> destinations = Arrays.asList(0);
            int numThreads = 1;
            
            List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
            assertEquals(Arrays.asList(0), result);
        }
        
        // Empty destinations list
        {
            int n = 5;
            List<int[]> edges = Arrays.asList(new int[]{0, 1, 1}, new int[]{1, 2, 1});
            int sourceNode = 0;
            List<Integer> destinations = new ArrayList<>();
            int numThreads = 2;
            
            List<Integer> result = solver.findShortestPaths(n, edges, sourceNode, destinations, numThreads);
            assertEquals(new ArrayList<>(), result);
        }
    }
}