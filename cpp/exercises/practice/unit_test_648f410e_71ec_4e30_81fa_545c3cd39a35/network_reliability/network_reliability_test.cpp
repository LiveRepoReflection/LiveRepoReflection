#include "network_reliability.h"
#include "catch.hpp"
#include <cmath>
#include <vector>
#include <tuple>

TEST_CASE("Single node graph", "[network_reliability]") {
    int n = 1;
    std::vector<std::tuple<int, int, double>> edges;
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - 1.0) < 1e-6);
}

TEST_CASE("Two nodes with operational probability 0.5", "[network_reliability]") {
    int n = 2;
    std::vector<std::tuple<int, int, double>> edges = { {0, 1, 0.5} };
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - 0.5) < 1e-6);
}

TEST_CASE("Two nodes with operational probability 0", "[network_reliability]") {
    int n = 2;
    std::vector<std::tuple<int, int, double>> edges = { {0, 1, 0.0} };
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - 0.0) < 1e-6);
}

TEST_CASE("Triangle graph with varying probabilities", "[network_reliability]") {
    int n = 3;
    // Edges: (0,1, 0.9), (1,2, 0.8), (0,2, 0.7)
    std::vector<std::tuple<int, int, double>> edges = { {0, 1, 0.9}, {1, 2, 0.8}, {0, 2, 0.7} };
    double expected = 0.902; // Precomputed expected probability
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - expected) < 1e-6);
}

TEST_CASE("Star graph with center node connectivity", "[network_reliability]") {
    int n = 4;
    // Star graph with node 0 as center connecting to nodes 1, 2, 3
    std::vector<std::tuple<int, int, double>> edges = { {0, 1, 0.5}, {0, 2, 0.5}, {0, 3, 0.5} };
    // The network is connected only if all edges are operational.
    double expected = 0.5 * 0.5 * 0.5;
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - expected) < 1e-6);
}

TEST_CASE("Cycle graph connectivity", "[network_reliability]") {
    int n = 4;
    // Cycle graph: (0,1), (1,2), (2,3), (3,0) with probability 0.6 each.
    std::vector<std::tuple<int, int, double>> edges = {
        {0, 1, 0.6}, {1, 2, 0.6}, {2, 3, 0.6}, {3, 0, 0.6}
    };
    // Connected if no edge fails or exactly one edge fails:
    double no_fail = 0.6 * 0.6 * 0.6 * 0.6;
    double one_fail = 4 * (0.6 * 0.6 * 0.6 * 0.4);
    double expected = no_fail + one_fail;
    double result = network_reliability::compute_network_reliability(n, edges);
    REQUIRE(std::abs(result - expected) < 1e-6);
}