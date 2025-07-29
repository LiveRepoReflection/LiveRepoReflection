package network_optimize;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import java.util.List;
import java.util.Arrays;
import java.util.ArrayList;

public class NetworkOptimizeTest {

    @Test
    public void testBasicExample() {
        int n = 4;
        int[] capacities = {20, 20, 20, 20};
        int[] traffic = {-5, 5, 0, 0};
        List<List<Integer>> edges = new ArrayList<>();
        edges.add(Arrays.asList(0, 1));
        edges.add(Arrays.asList(1, 2));
        edges.add(Arrays.asList(0, 3));
        edges.add(Arrays.asList(3, 2));
        int[] delays = {1, 1, 1, 1};

        int expected = 5;
        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(expected, result);
    }

    @Test
    public void testNoEdgesFeasible() {
        int n = 2;
        int[] capacities = {5, 5};
        int[] traffic = {-3, 3};
        List<List<Integer>> edges = new ArrayList<>();
        // With no edges, routing traffic is impossible.
        int[] delays = {1, 1};

        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(-1, result);
    }

    @Test
    public void testSingleRouterNoRouting() {
        int n = 1;
        int[] capacities = {10};
        int[] traffic = {0};
        List<List<Integer>> edges = new ArrayList<>();
        int[] delays = {1};

        int expected = 0;
        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(expected, result);
    }

    @Test
    public void testComplexSplitting() {
        // Network with a source at router 0 (-10) and sink at router 3 (+10)
        // Intermediaries (routers 1 and 2) allow splitting of the traffic.
        int n = 4;
        int[] capacities = {15, 15, 15, 15};
        int[] traffic = {-10, 0, 0, 10};
        List<List<Integer>> edges = new ArrayList<>();
        edges.add(Arrays.asList(0, 1));
        edges.add(Arrays.asList(0, 2));
        edges.add(Arrays.asList(1, 3));
        edges.add(Arrays.asList(2, 3));
        int[] delays = {2, 1, 1, 2};

        // In an optimal split, each path carries 5 units,
        // so the maximum load on any router (including source and sink) is 10.
        int expected = 10;
        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(expected, result);
    }

    @Test
    public void testInfeasibleDueToCapacity() {
        // In this network, the capacity is too low to accommodate the necessary flow.
        int n = 3;
        int[] capacities = {4, 4, 4};
        int[] traffic = {-5, 3, 2};
        List<List<Integer>> edges = new ArrayList<>();
        edges.add(Arrays.asList(0, 1));
        edges.add(Arrays.asList(1, 2));
        int[] delays = {1, 1, 1};

        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(-1, result);
    }

    @Test
    public void testDelayMinimization() {
        // Two potential routes from source to sink with different delay costs.
        // Router 0: source (-8) and Router 4: sink (+8)
        // Route 1: 0 -> 1 -> 4 with delay cost: delays[0] + delays[1] + delays[4]
        // Route 2: 0 -> 2 -> 3 -> 4 with delay cost: delays[0] + delays[2] + delays[3] + delays[4]
        int n = 5;
        int[] capacities = {10, 10, 10, 10, 10};
        int[] traffic = {-8, 0, 0, 0, 8};
        List<List<Integer>> edges = new ArrayList<>();
        edges.add(Arrays.asList(0, 1));
        edges.add(Arrays.asList(1, 4));
        edges.add(Arrays.asList(0, 2));
        edges.add(Arrays.asList(2, 3));
        edges.add(Arrays.asList(3, 4));
        int[] delays = {2, 5, 1, 1, 2};

        // The optimal strategy should minimize the overall delay while balancing the load.
        // In this setup, the maximum load is expected to be 8.
        int expected = 8;
        int result = NetworkOptimize.optimize(n, capacities, traffic, edges, delays);
        Assertions.assertEquals(expected, result);
    }
}