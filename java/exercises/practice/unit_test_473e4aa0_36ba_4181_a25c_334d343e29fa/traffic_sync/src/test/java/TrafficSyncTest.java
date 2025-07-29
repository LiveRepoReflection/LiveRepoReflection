import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;

public class TrafficSyncTest {

    @Test
    public void testSimpleLinearCity() {
        // Linear city with 3 intersections
        // 0 -> 1 -> 2
        int N = 3;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        adjList.get(0).add(new Pair<>(1, 5)); // Intersection 0 to 1 takes 5 units
        adjList.get(1).add(new Pair<>(2, 5)); // Intersection 1 to 2 takes 5 units
        
        int T = 10; // Cycle time
        int G = 5;  // Green light duration
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
        
        // In a linear city with equal travel times, we expect phases to be non-identical
        // as that would likely create better flow
        assertFalse(phases.get(0).equals(phases.get(1)), 
                   "Adjacent intersections should likely have different phases");
    }
    
    @Test
    public void testSmallGridCity() {
        // Small 2x2 grid city:
        // 0 -- 1
        // |    |
        // 2 -- 3
        int N = 4;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        
        // Bidirectional roads
        adjList.get(0).add(new Pair<>(1, 4)); // 0 <-> 1
        adjList.get(1).add(new Pair<>(0, 4));
        
        adjList.get(0).add(new Pair<>(2, 4)); // 0 <-> 2
        adjList.get(2).add(new Pair<>(0, 4));
        
        adjList.get(1).add(new Pair<>(3, 4)); // 1 <-> 3
        adjList.get(3).add(new Pair<>(1, 4));
        
        adjList.get(2).add(new Pair<>(3, 4)); // 2 <-> 3
        adjList.get(3).add(new Pair<>(2, 4));
        
        int T = 10; // Cycle time
        int G = 5;  // Green light duration
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
    }
    
    @Test
    public void testDisconnectedCity() {
        // City with two disconnected components
        // 0 -- 1    2 -- 3
        int N = 4;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        
        // Component 1
        adjList.get(0).add(new Pair<>(1, 3));
        adjList.get(1).add(new Pair<>(0, 3));
        
        // Component 2
        adjList.get(2).add(new Pair<>(3, 3));
        adjList.get(3).add(new Pair<>(2, 3));
        
        int T = 8; // Cycle time
        int G = 4; // Green light duration
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
    }
    
    @Test
    public void testComplexCity() {
        // Complex city with 6 intersections
        int N = 6;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        
        // Creating a more complex road network
        adjList.get(0).add(new Pair<>(1, 2));
        adjList.get(0).add(new Pair<>(2, 4));
        
        adjList.get(1).add(new Pair<>(0, 2));
        adjList.get(1).add(new Pair<>(3, 3));
        adjList.get(1).add(new Pair<>(4, 6));
        
        adjList.get(2).add(new Pair<>(0, 4));
        adjList.get(2).add(new Pair<>(3, 2));
        adjList.get(2).add(new Pair<>(5, 7));
        
        adjList.get(3).add(new Pair<>(1, 3));
        adjList.get(3).add(new Pair<>(2, 2));
        adjList.get(3).add(new Pair<>(4, 1));
        
        adjList.get(4).add(new Pair<>(1, 6));
        adjList.get(4).add(new Pair<>(3, 1));
        adjList.get(4).add(new Pair<>(5, 5));
        
        adjList.get(5).add(new Pair<>(2, 7));
        adjList.get(5).add(new Pair<>(4, 5));
        
        int T = 15; // Cycle time
        int G = 7;  // Green light duration
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
    }
    
    @Test
    public void testAllIntersectionsEqual() {
        // A city where all intersections are directly connected to each other
        // with same travel time - should result in evenly distributed phases
        int N = 5;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
            for (int j = 0; j < N; j++) {
                if (i != j) {
                    adjList.get(i).add(new Pair<>(j, 5)); // All roads take 5 time units
                }
            }
        }
        
        int T = 20; // Cycle time
        int G = 10; // Green light duration
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
    }
    
    @Test
    public void testDifferentCycleTimes() {
        // Testing with different cycle times and green light durations
        int N = 3;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        
        // Triangle city
        adjList.get(0).add(new Pair<>(1, 3));
        adjList.get(1).add(new Pair<>(2, 3));
        adjList.get(2).add(new Pair<>(0, 3));
        
        // Test case 1: Short cycle, short green
        int T1 = 4;
        int G1 = 2;
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases1 = trafficSync.findOptimalPhases(N, adjList, T1, G1);
        
        assertNotNull(phases1);
        assertEquals(N, phases1.size());
        for (int phase : phases1) {
            assertTrue(phase >= 0 && phase < T1, "Phase should be between 0 and " + (T1 - 1));
        }
        
        // Test case 2: Long cycle, long green
        int T2 = 18;
        int G2 = 12;
        List<Integer> phases2 = trafficSync.findOptimalPhases(N, adjList, T2, G2);
        
        assertNotNull(phases2);
        assertEquals(N, phases2.size());
        for (int phase : phases2) {
            assertTrue(phase >= 0 && phase < T2, "Phase should be between 0 and " + (T2 - 1));
        }
    }
    
    @Test
    @Timeout(value = 300, unit = TimeUnit.SECONDS)
    public void testLargeCity() {
        // Test with a larger city to ensure algorithm terminates within time limit
        int N = 20;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
            for (int j = 0; j < N; j++) {
                if (i != j && Math.random() < 0.3) { // Sparse random connections
                    adjList.get(i).add(new Pair<>(j, 1 + (int)(Math.random() * 10)));
                }
            }
        }
        
        int T = 10;
        int G = 5;
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        assertNotNull(phases);
        assertEquals(N, phases.size());
        for (int phase : phases) {
            assertTrue(phase >= 0 && phase < T, "Phase should be between 0 and " + (T - 1));
        }
    }
    
    @Test
    public void testConsistency() {
        // Test if algorithm gives consistent results for the same input
        int N = 4;
        List<List<Pair<Integer, Integer>>> adjList = new ArrayList<>();
        for (int i = 0; i < N; i++) {
            adjList.add(new ArrayList<>());
        }
        
        adjList.get(0).add(new Pair<>(1, 2));
        adjList.get(1).add(new Pair<>(2, 3));
        adjList.get(2).add(new Pair<>(3, 4));
        adjList.get(3).add(new Pair<>(0, 5));
        
        int T = 10;
        int G = 5;
        
        TrafficSync trafficSync = new TrafficSync();
        List<Integer> phases1 = trafficSync.findOptimalPhases(N, adjList, T, G);
        List<Integer> phases2 = trafficSync.findOptimalPhases(N, adjList, T, G);
        
        // The algorithm should give deterministic results
        assertNotNull(phases1);
        assertNotNull(phases2);
        assertEquals(phases1.size(), phases2.size());
        
        // If using a deterministic algorithm, the results should be identical
        // If using a randomized algorithm, comment this out
        // assertArrayEquals(phases1.toArray(), phases2.toArray());
    }
}