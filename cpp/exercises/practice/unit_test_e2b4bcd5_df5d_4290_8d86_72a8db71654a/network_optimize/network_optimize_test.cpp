#include <stdexcept>
#include <vector>
#include <cmath>
#include "catch.hpp"
#include "network_optimize.h"

using std::vector;

static const double TOLERANCE = 1e-6;

TEST_CASE("Two nodes, K = 0", "[network_optimize]") {
    int N = 2;
    int K = 0;
    vector<vector<int>> adjMatrix = {
        {0, 3},
        {3, 0}
    };

    // Only one pair: distance 3.
    double expected_avg = 3.0;
    double result = network_optimize::optimize_network(N, adjMatrix, K);
    REQUIRE(std::abs(result - expected_avg) < TOLERANCE);
}

TEST_CASE("Three nodes, K = 1 (no improvement possible)", "[network_optimize]") {
    int N = 3;
    int K = 1;
    // Graph:
    // 0 <-> 1 (5), 0 <-> 2 (100), 1 <-> 2 (50)
    vector<vector<int>> adjMatrix = {
        {0,   5, 100},
        {5,   0,  50},
        {100, 50,   0}
    };

    // Compute shortest distances:
    // 0-1: 5
    // 0-2: min(100, 0-1-2 = 5+50 = 55) = 55
    // 1-2: 50
    // Average = (5 + 55 + 50) / 3 = 110/3 ≈ 36.666666667
    double expected_avg = 110.0 / 3.0;
    double result = network_optimize::optimize_network(N, adjMatrix, K);
    REQUIRE(std::abs(result - expected_avg) < TOLERANCE);
}

TEST_CASE("Four nodes, K = 1", "[network_optimize]") {
    int N = 4;
    int K = 1;
    // Graph with one promising candidate:
    // The direct edge weights are such that the common node can lower distances.
    // Matrix:
    //   0: [0,   600, 600,  50]
    //   1: [600,   0, 600,  50]
    //   2: [600, 600,   0,  50]
    //   3: [50,   50,  50,   0]
    //
    // Without accelerator optimization, the all-pairs shortest distances become:
    // 0-1: via node 3: 50 + 50 = 100
    // 0-2: 100, 0-3: 50
    // 1-2: 100, 1-3: 50, 2-3: 50
    // Sum = 100+100+50+100+50+50 = 450, average = 450/6 = 75.
    double expected_avg = 75.0;
    vector<vector<int>> adjMatrix = {
        {0,   600, 600,  50},
        {600,   0, 600,  50},
        {600, 600,   0,  50},
        {50,   50,  50,   0}
    };

    double result = network_optimize::optimize_network(N, adjMatrix, K);
    REQUIRE(std::abs(result - expected_avg) < TOLERANCE);
}

TEST_CASE("Four nodes, K = 2", "[network_optimize]") {
    int N = 4;
    int K = 2;
    // Use the same matrix as before.
    // With additional accelerator node available, the optimum should not be worse than the K=1 case.
    // Expected average remains 75 due to the structure of the matrix.
    double expected_avg = 75.0;
    vector<vector<int>> adjMatrix = {
        {0,   600, 600,  50},
        {600,   0, 600,  50},
        {600, 600,   0,  50},
        {50,   50,  50,   0}
    };

    double result = network_optimize::optimize_network(N, adjMatrix, K);
    REQUIRE(std::abs(result - expected_avg) < TOLERANCE);
}

TEST_CASE("Disconnected network remains unreachable", "[network_optimize]") {
    int N = 3;
    int K = 1;
    // Disconnected graph: no edges between any distinct nodes.
    vector<vector<int>> adjMatrix = {
        {0, -1, -1},
        {-1, 0, -1},
        {-1, -1, 0}
    };

    // Since the network is disconnected, even after deploying accelerators,
    // some pairs remain unreachable. The specification requires that in such cases,
    // the function throws an exception.
    REQUIRE_THROWS_AS(network_optimize::optimize_network(N, adjMatrix, K), std::invalid_argument);
}