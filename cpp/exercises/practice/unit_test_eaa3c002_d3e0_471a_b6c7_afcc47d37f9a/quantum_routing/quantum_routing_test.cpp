#include <vector>
#include "catch.hpp"
#include "quantum_routing.h"

using std::vector;

TEST_CASE("Source equals Destination", "[quantum_routing]") {
    int N = 1;
    vector<vector<double>> channel_probabilities = {
        {1.0}
    };
    int S = 0;
    int D = 0;
    int max_attempts = 10;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    vector<int> expected = {0};
    REQUIRE(path == expected);
}

TEST_CASE("Direct High Probability Route", "[quantum_routing]") {
    int N = 2;
    vector<vector<double>> channel_probabilities = {
        {1.0, 0.9},
        {0.9, 1.0}
    };
    int S = 0;
    int D = 1;
    int max_attempts = 5;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    // The direct route is expected when the channel is reliable.
    vector<int> expected = {0, 1};
    REQUIRE(path == expected);
}

TEST_CASE("Indirect Route is More Optimal", "[quantum_routing]") {
    int N = 3;
    // Graph representation:
    // 0-1: 0.8, 1-2: 0.8, 0-2: 0.2.
    // Although there is a direct route, optimal expected teleportation steps are lower via 0->1->2.
    vector<vector<double>> channel_probabilities = {
        {1.0, 0.8, 0.2},
        {0.8, 1.0, 0.8},
        {0.2, 0.8, 1.0}
    };
    int S = 0;
    int D = 2;
    int max_attempts = 10;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    vector<int> expected = {0, 1, 2};
    REQUIRE(path == expected);
}

TEST_CASE("No Valid Route", "[quantum_routing]") {
    int N = 3;
    // No connectivity between distinct nodes.
    vector<vector<double>> channel_probabilities = {
        {1.0, 0.0, 0.0},
        {0.0, 1.0, 0.0},
        {0.0, 0.0, 1.0}
    };
    int S = 0;
    int D = 2;
    int max_attempts = 5;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    REQUIRE(path.empty());
}

TEST_CASE("Complex Network with Cycles", "[quantum_routing]") {
    int N = 5;
    // Graph structure:
    // 0 <-> 1 (0.6), 1 <-> 2 (0.6), 2 <-> 4 (0.6)
    // 0 <-> 3 (0.9), 3 <-> 4 (0.9)
    // Additionally, extra connections to form cycles.
    // Optimal path is expected to be [0, 3, 4] due to higher channel probabilities.
    vector<vector<double>> channel_probabilities = {
        {1.0, 0.6, 0.0, 0.9, 0.0},
        {0.6, 1.0, 0.6, 0.0, 0.0},
        {0.0, 0.6, 1.0, 0.0, 0.6},
        {0.9, 0.0, 0.0, 1.0, 0.9},
        {0.0, 0.0, 0.6, 0.9, 1.0}
    };
    int S = 0;
    int D = 4;
    int max_attempts = 20;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    vector<int> expected = {0, 3, 4};
    REQUIRE(path == expected);
}

TEST_CASE("Multiple Paths with Trade-Offs", "[quantum_routing]") {
    int N = 4;
    // Graph structure:
    // 0 <-> 1: 0.7, 1 <-> 3: 0.7, producing expected steps ~ (1/0.7 + 1/0.7)
    // Alternative: 0 <-> 2: 0.9, 2 <-> 3: 0.4, producing expected steps ~ (1/0.9 + 1/0.4)
    // Optimal path is expected to be [0, 1, 3].
    vector<vector<double>> channel_probabilities = {
        {1.0, 0.7, 0.9, 0.0},
        {0.7, 1.0, 0.0, 0.7},
        {0.9, 0.0, 1.0, 0.4},
        {0.0, 0.7, 0.4, 1.0}
    };
    int S = 0;
    int D = 3;
    int max_attempts = 15;
    vector<int> path = quantumRouting(N, channel_probabilities, S, D, max_attempts);
    vector<int> expected = {0, 1, 3};
    REQUIRE(path == expected);
}