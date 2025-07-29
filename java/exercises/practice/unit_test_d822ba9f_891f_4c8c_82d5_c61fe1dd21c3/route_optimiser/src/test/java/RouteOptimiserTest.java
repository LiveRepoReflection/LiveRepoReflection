import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertIterableEquals;
import java.util.List;
import java.util.ArrayList;

public class RouteOptimiserTest {

    // Helper method to create an edge represented by an int array: {u, v, time, toll}
    private int[] edge(int u, int v, int time, int toll) {
        return new int[] { u, v, time, toll };
    }

    @Test
    @DisplayName("Test single direct route from depot to destination")
    public void testDirectRoute() {
        int N = 2;
        List<int[]> edges = new ArrayList<>();
        // direct edge from 0 to 1 with time 10 and toll 5
        edges.add(edge(0, 1, 10, 5));
        List<Integer> destinations = new ArrayList<>();
        destinations.add(1);
        int timeWeight = 2;
        int tollWeight = 3;
        // expected weighted cost is (2*10 + 3*5) = 20 + 15 = 35
        List<Double> expected = List.of(35.0);
        List<Double> result = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected.size(), result.size(), "Result size mismatch");
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i), result.get(i), 1e-6, "Mismatch at destination index " + i);
        }
    }

    @Test
    @DisplayName("Test multiple paths with trade-offs in time and toll")
    public void testMultiplePaths() {
        int N = 3;
        List<int[]> edges = new ArrayList<>();
        // Two possible ways from 0 to 2:
        // Path 1: direct edge 0 -> 2 (time=25, toll=2)
        edges.add(edge(0, 2, 25, 2));
        // Path 2: 0 -> 1 -> 2: total time = 10+10=20, total toll = 5+5=10
        edges.add(edge(0, 1, 10, 5));
        edges.add(edge(1, 2, 10, 5));
        List<Integer> destinations = List.of(2);

        // Test scenario 1: prioritize time over toll: timeWeight=3, tollWeight=1
        // For path 1: 3*25+1*2 = 75+2 = 77, for path 2: 3*20+1*10 = 60+10 = 70 -> choose path 2
        int timeWeight = 3;
        int tollWeight = 1;
        List<Double> expected1 = List.of(70.0);
        List<Double> result1 = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected1.size(), result1.size(), "Result size mismatch for scenario1");
        for (int i = 0; i < expected1.size(); i++) {
            assertEquals(expected1.get(i), result1.get(i), 1e-6, "Mismatch at destination index " + i + " for scenario1");
        }

        // Test scenario 2: prioritize toll over time: timeWeight=1, tollWeight=3
        // For path 1: 1*25+3*2 = 25+6 = 31, for path 2: 1*20+3*10 = 20+30 = 50 -> choose path 1
        timeWeight = 1;
        tollWeight = 3;
        List<Double> expected2 = List.of(31.0);
        List<Double> result2 = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected2.size(), result2.size(), "Result size mismatch for scenario2");
        for (int i = 0; i < expected2.size(); i++) {
            assertEquals(expected2.get(i), result2.get(i), 1e-6, "Mismatch at destination index " + i + " for scenario2");
        }
    }

    @Test
    @DisplayName("Test unreachable destination returns -1.0")
    public void testUnreachableDestination() {
        int N = 3;
        List<int[]> edges = new ArrayList<>();
        // Graph has an edge from 0 -> 1 only; destination 2 is unreachable.
        edges.add(edge(0, 1, 15, 5));
        List<Integer> destinations = List.of(2);
        int timeWeight = 2;
        int tollWeight = 2;
        List<Double> expected = List.of(-1.0);
        List<Double> result = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected.size(), result.size(), "Result size mismatch");
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i), result.get(i), 1e-6, "Mismatch for unreachable destination at index " + i);
        }
    }

    @Test
    @DisplayName("Test graph with cycles is handled correctly")
    public void testCycleHandling() {
        int N = 4;
        List<int[]> edges = new ArrayList<>();
        // Create a cycle: 0 -> 1 -> 2 -> 1, and edge from 2 -> 3 leads to destination.
        edges.add(edge(0, 1, 5, 1));
        edges.add(edge(1, 2, 5, 1));
        edges.add(edge(2, 1, 1, 0)); // cycle edge reducing time cost slightly
        edges.add(edge(2, 3, 10, 5));
        List<Integer> destinations = List.of(3);
        int timeWeight = 2;
        int tollWeight = 1;
        // The optimal route is 0->1->2->3 even with the cycle available. 
        // Even if cycle exists, taking it repeatedly will not yield any benefit since weights are positive.
        // Expected cost: 0->1:2*5+1*1 =10+1=11, 1->2:2*5+1*1=10+1=11, 2->3:2*10+1*5=20+5=25, total=11+11+25=47.
        List<Double> expected = List.of(47.0);
        List<Double> result = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected.size(), result.size(), "Result size mismatch for cycle test");
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i), result.get(i), 1e-6, "Mismatch at destination index " + i + " for cycle test");
        }
    }

    @Test
    @DisplayName("Test multiple destinations with mixed reachability")
    public void testMultipleDestinations() {
        int N = 5;
        List<int[]> edges = new ArrayList<>();
        // Graph structure:
        // 0 -> 1: time 5, toll 2
        // 1 -> 2: time 5, toll 2
        // 0 -> 3: time 15, toll 1
        // 3 -> 4: time 5, toll 2
        edges.add(edge(0, 1, 5, 2));
        edges.add(edge(1, 2, 5, 2));
        edges.add(edge(0, 3, 15, 1));
        edges.add(edge(3, 4, 5, 2));
        // Destination 2 is reachable, 4 is reachable, and 0 is the depot.
        List<Integer> destinations = List.of(0, 2, 4);
        int timeWeight = 1;
        int tollWeight = 1;
        // Expected:
        // For destination 0, cost is 0 (already at depot)
        // For destination 2, cost = (5+5)+(2+2)=10+4=14
        // For destination 4, cost = (15+5)+(1+2)=20+3=23
        List<Double> expected = List.of(0.0, 14.0, 23.0);
        List<Double> result = RouteOptimiser.findOptimalRoutes(N, edges, destinations, timeWeight, tollWeight);
        assertEquals(expected.size(), result.size(), "Result size mismatch for multiple destinations");
        for (int i = 0; i < expected.size(); i++) {
            assertEquals(expected.get(i), result.get(i), 1e-6, "Mismatch at destination index " + i + " for multiple destinations");
        }
    }
}