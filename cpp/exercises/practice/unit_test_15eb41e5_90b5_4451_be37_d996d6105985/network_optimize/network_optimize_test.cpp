#include "network_optimize.h"
#include "catch.hpp"
#include <vector>

using namespace network_optimize;

TEST_CASE("no edges - graph not connected", "[optimal_network_bandwidth]") {
    int n = 3;
    std::vector<Edge> edges; // No edges provided, hence cannot connect all nodes.
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 0);
}

TEST_CASE("single edge - trivial connected graph", "[optimal_network_bandwidth]") {
    int n = 2;
    std::vector<Edge> edges = {
        {0, 1, 5, 10}
    };
    // Only one pair exists (0,1) with bottleneck bandwidth = 10.
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 10);
}

TEST_CASE("sample example", "[optimal_network_bandwidth]") {
    int n = 3;
    std::vector<Edge> edges = {
        {0, 1, 10, 50},
        {0, 2, 20, 30},
        {1, 2, 5, 80}
    };
    // Expected optimal configuration gives:
    // For 0-1: bottleneck = 50,
    // For 1-2: bottleneck = 80,
    // For 0-2: optimal path 0-1-2 with latency 10+5=15 and bottleneck = min(50,80) = 50.
    // Overall minimum is 50.
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 50);
}

TEST_CASE("complex network configuration", "[optimal_network_bandwidth]") {
    int n = 4;
    std::vector<Edge> edges = {
        {0, 1, 10, 40},
        {1, 2, 10, 60},
        {2, 3, 10, 80},
        {0, 3, 30, 100},
        {1, 3, 20, 50}
    };
    // One optimal configuration is picking edges {0,1}, {1,2}, {2,3}.
    // Then bottlenecks:
    // 0-1: 40, 0-2: min(40,60)=40, 0-3: min(40,60,80)=40, 1-2: 60, 1-3: min(60,80)=60, 2-3:80.
    // The minimum among all pairs is 40.
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 40);
}

TEST_CASE("non-connected graph", "[optimal_network_bandwidth]") {
    int n = 4;
    std::vector<Edge> edges = {
        {0, 1, 5, 50},
        {2, 3, 5, 50}
    };
    // The graph has two disconnected components, so it is not possible to connect all nodes.
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 0);
}

TEST_CASE("tie scenario with multiple minimum latency paths", "[optimal_network_bandwidth]") {
    int n = 4;
    std::vector<Edge> edges = {
        {0, 1, 5, 50},
        {1, 3, 5, 30},
        {0, 3, 10, 60},
        {1, 2, 5, 100},
        {2, 3, 5, 20}
    };
    /* Analysis:
       For pair (0,3):
         Path 1: 0-1-3 has latency = 5 + 5 = 10, bottleneck = min(50, 30) = 30.
         Path 2: direct edge 0-3 has latency = 10, bottleneck = 60.
         Minimum latency is 10 for both, so we consider the best bottleneck value among paths with minimum latency, which is 60.
       For other pairs:
         0-1: 50, 1-2: 100, 2-3: 20, 0-2: path 0-1-2 = min(50,100) = 50, 1-3: 30.
       The overall minimum among all pairs is min(50, 60, 50, 100, 30, 20) = 20.
    */
    int result = optimal_network_bandwidth(n, edges);
    REQUIRE(result == 20);
}