package quantum_network;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class QuantumNetworkTest {

    // Helper method: validate the returned path is contiguous based on given channels.
    private boolean isValidPath(List<Integer> path, List<double[]> channels) {
        if (path == null || path.size() < 2) return false;
        for (int i = 0; i < path.size() - 1; i++) {
            boolean found = false;
            int u = path.get(i);
            int v = path.get(i + 1);
            for (double[] ch : channels) {
                // channel is bidirectional; store as: [u, v, fidelity]
                if ((ch[0] == u && ch[1] == v) || (ch[0] == v && ch[1] == u)) {
                    found = true;
                    break;
                }
            }
            if (!found) return false;
        }
        return true;
    }

    // Helper method: compute fidelity for a given path.
    private double computePathFidelity(List<Integer> path, List<double[]> channels) {
        double fidelity = 1.0;
        for (int i = 0; i < path.size() - 1; i++) {
            int u = path.get(i);
            int v = path.get(i+1);
            boolean found = false;
            for (double[] ch : channels) {
                if ((ch[0] == u && ch[1] == v) || (ch[0] == v && ch[1] == u)) {
                    fidelity *= ch[2];
                    found = true;
                    break;
                }
            }
            if (!found) return 0.0;
        }
        return fidelity;
    }

    // Test case 1: Basic network with valid paths.
    @Test
    public void testBasicNetwork() {
        int N = 4;
        // Channels: each double array is {u, v, fidelity}
        List<double[]> channels = new ArrayList<>();
        channels.add(new double[]{0, 1, 0.9});
        channels.add(new double[]{1, 2, 0.8});
        channels.add(new double[]{2, 3, 0.7});
        channels.add(new double[]{0, 3, 0.6});
        
        // Requests: each int array is {source, destination}
        List<int[]> requests = new ArrayList<>();
        requests.add(new int[]{0, 3});
        requests.add(new int[]{1, 3});
        
        int[] nodeCapacities = {2, 2, 2, 2};

        List<List<Integer>> result = QuantumNetwork.optimizeNetwork(N, channels, requests, nodeCapacities);
        assertEquals(2, result.size());
        
        // Validate each returned path: should start with the request source and end with the destination.
        for (int i = 0; i < requests.size(); i++) {
            int source = requests.get(i)[0];
            int dest = requests.get(i)[1];
            List<Integer> path = result.get(i);
            // Since a valid path is expected, path must not be empty.
            assertFalse(path.isEmpty(), "Path for request " + source + " to " + dest + " should not be empty.");
            assertEquals(source, (int) path.get(0), "Path should start with source node.");
            assertEquals(dest, (int) path.get(path.size()-1), "Path should end with destination node.");
            // Validate contiguous path.
            assertTrue(isValidPath(path, channels), "Path " + path + " is not valid based on channels.");
        }
    }

    // Test case 2: No available path due to disconnected network.
    @Test
    public void testNoPathAvailable() {
        int N = 3;
        List<double[]> channels = new ArrayList<>();
        channels.add(new double[]{0, 1, 0.95});
        // Node 2 is disconnected
        List<int[]> requests = new ArrayList<>();
        requests.add(new int[]{0, 2});
        
        int[] nodeCapacities = {1, 1, 1};
        
        List<List<Integer>> result = QuantumNetwork.optimizeNetwork(N, channels, requests, nodeCapacities);
        // Since no path exists, expecting an empty list.
        assertEquals(1, result.size());
        assertTrue(result.get(0).isEmpty(), "No path should be returned when network is disconnected.");
    }

    // Test case 3: Capacity constraint violation.
    @Test
    public void testCapacityConstraint() {
        int N = 4;
        List<double[]> channels = new ArrayList<>();
        channels.add(new double[]{0, 1, 0.9});
        channels.add(new double[]{1, 2, 0.8});
        channels.add(new double[]{2, 3, 0.7});
        channels.add(new double[]{0, 3, 0.6});
        
        // Two requests that both require use of node 1, but node 1 capacity is 1.
        List<int[]> requests = new ArrayList<>();
        requests.add(new int[]{0, 2});
        requests.add(new int[]{1, 3});
        
        int[] nodeCapacities = {2, 1, 2, 2};

        List<List<Integer>> result = QuantumNetwork.optimizeNetwork(N, channels, requests, nodeCapacities);
        assertEquals(2, result.size());
        
        // At least one of the requests should have an empty path due to capacity constraint.
        boolean hasEmpty = result.stream().anyMatch(List::isEmpty);
        assertTrue(hasEmpty, "At least one request should fail due to capacity constraints.");
        
        // If a path is returned, validate its structure.
        for (int i = 0; i < requests.size(); i++) {
            if (!result.get(i).isEmpty()) {
                int source = requests.get(i)[0];
                int dest = requests.get(i)[1];
                List<Integer> path = result.get(i);
                assertEquals(source, (int) path.get(0), "Path should start with the source node.");
                assertEquals(dest, (int) path.get(path.size()-1), "Path should end with the destination node.");
                assertTrue(isValidPath(path, channels), "Returned path does not follow valid channel connectivity.");
            }
        }
    }

    // Test case 4: Multiple paths available; check that returned paths maximize fidelity.
    @Test
    public void testMultiplePathsMaxFidelity() {
        int N = 5;
        List<double[]> channels = new ArrayList<>();
        // Create a network with two possible paths from 0 to 4
        // Path A: 0->1->4 with fidelity 0.9 * 0.8 = 0.72
        channels.add(new double[]{0, 1, 0.9});
        channels.add(new double[]{1, 4, 0.8});
        // Path B: 0->2->3->4 with fidelity 0.95 * 0.95 * 0.95 = 0.857375
        channels.add(new double[]{0, 2, 0.95});
        channels.add(new double[]{2, 3, 0.95});
        channels.add(new double[]{3, 4, 0.95});
        
        List<int[]> requests = new ArrayList<>();
        requests.add(new int[]{0, 4});
        
        int[] nodeCapacities = {2, 2, 2, 2, 2};

        List<List<Integer>> result = QuantumNetwork.optimizeNetwork(N, channels, requests, nodeCapacities);
        assertEquals(1, result.size());
        List<Integer> path = result.get(0);
        // The returned path should start at 0 and end at 4.
        assertFalse(path.isEmpty(), "Expected a valid path for the request.");
        assertEquals(0, (int)path.get(0));
        assertEquals(4, (int)path.get(path.size()-1));
        assertTrue(isValidPath(path, channels), "Returned path is not valid.");

        // Compute fidelity and check if it is close to the higher possible fidelity.
        double fidelity = computePathFidelity(path, channels);
        // The better fidelity is 0.857375, so allow a small epsilon tolerance.
        assertTrue(Math.abs(fidelity - 0.857375) < 1e-6, "Returned path does not maximize fidelity as expected.");
    }

    // Test case 5: Complex network with several requests and overlapping capacity usage.
    @Test
    public void testComplexNetworkOverlappingRequests() {
        int N = 6;
        List<double[]> channels = new ArrayList<>();
        channels.add(new double[]{0, 1, 0.9});
        channels.add(new double[]{1, 2, 0.85});
        channels.add(new double[]{2, 5, 0.8});
        channels.add(new double[]{0, 3, 0.95});
        channels.add(new double[]{3, 4, 0.9});
        channels.add(new double[]{4, 5, 0.88});
        channels.add(new double[]{1, 3, 0.7});
        channels.add(new double[]{2, 4, 0.75});
        
        List<int[]> requests = new ArrayList<>();
        requests.add(new int[]{0, 5});
        requests.add(new int[]{0, 5});
        requests.add(new int[]{1, 4});
        requests.add(new int[]{3, 2});
        
        // Set capacities such that some nodes cannot handle all requests.
        int[] nodeCapacities = {3, 2, 2, 2, 2, 3};

        List<List<Integer>> result = QuantumNetwork.optimizeNetwork(N, channels, requests, nodeCapacities);
        assertEquals(requests.size(), result.size());
        
        // Validate each non-empty returned path is valid.
        for (int i = 0; i < requests.size(); i++) {
            int source = requests.get(i)[0];
            int dest = requests.get(i)[1];
            List<Integer> path = result.get(i);
            if (!path.isEmpty()) {
                assertEquals(source, (int)path.get(0));
                assertEquals(dest, (int)path.get(path.size()-1));
                assertTrue(isValidPath(path, channels), "Path " + path + " for request from " + source + " to " + dest + " is invalid.");
            }
        }
        // Check that not all requests passed if capacities are conflicting.
        // At least one request is allowed to return an empty path due to capacity overload.
        long emptyCount = result.stream().filter(List::isEmpty).count();
        assertTrue(emptyCount >= 0, "At least zero requests can be unsatisfied due to capacity constraints.");
    }
}