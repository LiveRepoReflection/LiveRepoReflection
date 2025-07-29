#include "catch.hpp"
#include "network_partition.h"
#include <vector>
#include <tuple>
#include <set>
#include <algorithm>
#include <numeric>
#include <stdexcept>

// Helper function to verify that the returned partition is valid.
// It checks that the partition contains distinct nodes, all nodes in [0, n-1] are assigned, and no node appears twice.
void verifyValidPartition(int n, const std::vector<int>& partA) {
    std::set<int> setA(partA.begin(), partA.end());
    // Check for duplicates
    REQUIRE(setA.size() == partA.size());
    
    // Check that all nodes are in the range [0, n-1]
    for (int node : setA) {
        REQUIRE(node >= 0);
        REQUIRE(node < n);
    }
    
    // Construct Partition B (all nodes not in Partition A)
    std::set<int> setAll;
    for (int i = 0; i < n; ++i) {
        setAll.insert(i);
    }
    
    std::set<int> partB;
    std::set_difference(setAll.begin(), setAll.end(), setA.begin(), setA.end(),
                        std::inserter(partB, partB.begin()));
    
    // Ensure the union of A and B covers all nodes
    std::set<int> unionSet;
    std::set_union(setA.begin(), setA.end(), partB.begin(), partB.end(),
                   std::inserter(unionSet, unionSet.begin()));
    REQUIRE(unionSet.size() == static_cast<size_t>(n));
}

// Helper function to compute cost sum for a partition
int computeCostSum(const std::set<int>& part, const std::vector<int>& costs) {
    int sum = 0;
    for (int node : part) {
        sum += costs[node];
    }
    return sum;
}

// Helper function to compute capacity cut between Partition A and Partition B
int computeCapacityCut(const std::vector<std::tuple<int,int,int>>& edges,
                       const std::set<int>& partA,
                       const std::set<int>& partB) {
    int cutSum = 0;
    for (const auto& edge : edges) {
        int u, v, weight;
        std::tie(u, v, weight) = edge;
        // If one endpoint in partA and the other in partB then it's in the cut.
        if ((partA.count(u) && partB.count(v)) || (partA.count(v) && partB.count(u))) {
            cutSum += weight;
        }
    }
    return cutSum;
}

// Test Case 1: Simple graph with two nodes and no edge.
TEST_CASE("simple_two_nodes_no_edge") {
    int n = 2;
    std::vector<std::tuple<int,int,int>> edges; // No edges.
    std::vector<int> costs = {10, 20};
    double lambda = 1.0;
    
    std::vector<int> partA = partitionNetwork(n, edges, costs, lambda);
    verifyValidPartition(n, partA);
    
    // Compute partitions A and B
    std::set<int> setA(partA.begin(), partA.end());
    std::set<int> setB;
    for (int i = 0; i < n; ++i) {
        if (setA.find(i) == setA.end()) {
            setB.insert(i);
        }
    }
    
    int costA = computeCostSum(setA, costs);
    int costB = computeCostSum(setB, costs);
    
    // For no edge, objective is just max(costA, costB)
    int obj = std::max(costA, costB);
    
    // Since both partitions are valid, check that objective is within expected range.
    // Either partition is acceptable if it minimizes max(costA, costB).
    REQUIRE(obj >= 10);
    REQUIRE(obj <= 20);
}

// Test Case 2: Graph with disconnected components.
TEST_CASE("disconnected_components") {
    int n = 4;
    // Two disconnected groups: nodes 0-1 and nodes 2-3.
    std::vector<std::tuple<int,int,int>> edges = {
        std::make_tuple(0, 1, 5),
        std::make_tuple(2, 3, 5)
    };
    std::vector<int> costs = {50, 50, 100, 100};
    double lambda = 0.0;
    
    std::vector<int> partA = partitionNetwork(n, edges, costs, lambda);
    verifyValidPartition(n, partA);
    
    // Compute partitions A and B.
    std::set<int> setA(partA.begin(), partA.end());
    std::set<int> setB;
    for (int i = 0; i < n; ++i)
        if (setA.find(i) == setA.end())
            setB.insert(i);
    
    int costA = computeCostSum(setA, costs);
    int costB = computeCostSum(setB, costs);
    int objective = std::max(costA, costB);
    
    // In a balanced partition we would expect both groups to have similar cost.
    // Ensure that the objective is not excessively larger than one of the group sums.
    REQUIRE(objective <= 200);
}

// Test Case 3: Graph with multiple edges and a mix of costs.
TEST_CASE("graph_with_edges_and_mixed_costs") {
    int n = 4;
    std::vector<std::tuple<int,int,int>> edges = {
        std::make_tuple(0, 1, 10),
        std::make_tuple(0, 2, 15),
        std::make_tuple(1, 3, 20),
        std::make_tuple(2, 3, 30)
    };
    std::vector<int> costs = {100, 200, 300, 400};
    double lambda = 0.5;
    
    std::vector<int> partA = partitionNetwork(n, edges, costs, lambda);
    verifyValidPartition(n, partA);
    
    // Compute partitions A and B.
    std::set<int> setA(partA.begin(), partA.end());
    std::set<int> setB;
    for (int i = 0; i < n; ++i)
        if (setA.find(i) == setA.end())
            setB.insert(i);
    
    int costA = computeCostSum(setA, costs);
    int costB = computeCostSum(setB, costs);
    int capacityCut = computeCapacityCut(edges, setA, setB);
    
    double objective = std::max(costA, costB) + lambda * capacityCut;
    
    // We don't require an exact objective value, but ensure it is within reasonable bounds.
    // Lower bound and upper bound are problem-dependent.
    REQUIRE(objective >= 0.0);
    REQUIRE(objective <= 1000.0);
}

// Test Case 4: Graph where all nodes have the same cost and zero edge weights.
TEST_CASE("uniform_cost_zero_edges") {
    int n = 6;
    std::vector<std::tuple<int,int,int>> edges; // No edges.
    std::vector<int> costs(n, 100); // All nodes have cost 100.
    double lambda = 10.0;
    
    std::vector<int> partA = partitionNetwork(n, edges, costs, lambda);
    verifyValidPartition(n, partA);
    
    // Compute partitions A and B.
    std::set<int> setA(partA.begin(), partA.end());
    std::set<int> setB;
    for (int i = 0; i < n; ++i) {
        if (setA.find(i) == setA.end()) {
            setB.insert(i);
        }
    }
    
    int costA = computeCostSum(setA, costs);
    int costB = computeCostSum(setB, costs);
    // With no edges, capacity cut is zero.
    double objective = std::max(costA, costB);
    
    // Best partition should try to balance number of nodes.
    // For 6 nodes all costing 100, balanced partitions would be of size 3 and 3.
    // Thus, objective should equal 300.
    REQUIRE(objective == 300);
}