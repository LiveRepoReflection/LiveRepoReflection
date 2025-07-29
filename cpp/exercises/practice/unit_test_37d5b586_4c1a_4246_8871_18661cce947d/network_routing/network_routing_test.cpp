#include "catch.hpp"
#include "network_routing.h"
#include <vector>
#include <tuple>

using namespace std;
using namespace network_routing;

TEST_CASE("Basic example - optimal worst-case latency path", "[network_routing]") {
    int N = 5;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 5),
        make_tuple(0, 2, 3),
        make_tuple(1, 3, 6),
        make_tuple(2, 3, 4),
        make_tuple(3, 4, 2)
    };
    int src = 0;
    int dest = 4;
    int result = find_optimal_latency(N, edges, src, dest);
    // The path 0-2-3-4 has worst-case latency 4, which is optimal.
    REQUIRE(result == 4);
}

TEST_CASE("No possible path - disconnected graph", "[network_routing]") {
    int N = 4;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 3),
        make_tuple(1, 0, 3),
        make_tuple(2, 3, 4)
    };
    int src = 0;
    int dest = 3;
    int result = find_optimal_latency(N, edges, src, dest);
    // No connection exists between node 0 and node 3.
    REQUIRE(result == -1);
}

TEST_CASE("Single node graph", "[network_routing]") {
    int N = 1;
    vector<tuple<int, int, int>> edges; // empty edges
    int src = 0;
    int dest = 0;
    int result = find_optimal_latency(N, edges, src, dest);
    // With a single node, the worst-case latency is 0 since no edge is needed.
    REQUIRE(result == 0);
}

TEST_CASE("Multiple paths with different worst-case latencies", "[network_routing]") {
    int N = 6;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 10),
        make_tuple(1, 5, 10),
        make_tuple(0, 2, 5),
        make_tuple(2, 3, 7),
        make_tuple(3, 5, 6),
        make_tuple(0, 4, 6),
        make_tuple(4, 5, 12)
    };
    int src = 0;
    int dest = 5;
    int result = find_optimal_latency(N, edges, src, dest);
    // Possible paths:
    // 0-1-5: worst-case latency = max(10, 10) = 10.
    // 0-2-3-5: worst-case latency = max(5, 7, 6) = 7.
    // 0-4-5: worst-case latency = max(6, 12) = 12.
    // The optimal is 7.
    REQUIRE(result == 7);
}

TEST_CASE("Graph with cycle and redundant paths", "[network_routing]") {
    int N = 7;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 4),
        make_tuple(1, 2, 8),
        make_tuple(2, 3, 2),
        make_tuple(3, 4, 6),
        make_tuple(4, 5, 3),
        make_tuple(5, 1, 7),
        make_tuple(2, 6, 5),
        make_tuple(6, 4, 1)
    };
    int src = 0;
    int dest = 5;
    int result = find_optimal_latency(N, edges, src, dest);
    // Analyze possible paths:
    // Path 1: 0-1-2-3-4-5: worst-case latency = max(4, 8, 2, 6, 3) = 8.
    // Path 2: 0-1-2-6-4-5: worst-case latency = max(4, 8, 5, 1, 3) = 8.
    // Path 3: 0-1-5: worst-case latency = max(4,7) = 7.
    // The optimal worst-case latency is 7.
    REQUIRE(result == 7);
}

TEST_CASE("Multiple edges scenario with large latencies", "[network_routing]") {
    int N = 8;
    vector<tuple<int, int, int>> edges = {
        make_tuple(0, 1, 1000000000),
        make_tuple(0, 2, 500),
        make_tuple(1, 3, 600),
        make_tuple(2, 3, 700),
        make_tuple(3, 4, 800),
        make_tuple(4, 5, 900),
        make_tuple(5, 6, 1000),
        make_tuple(6, 7, 1100),
        make_tuple(2, 7, 1500)
    };
    int src = 0;
    int dest = 7;
    int result = find_optimal_latency(N, edges, src, dest);
    // Evaluate possible paths:
    // Path 1: 0-1-3-4-5-6-7: worst-case latency = max(1000000000,600,800,900,1000,1100) = 1000000000.
    // Path 2: 0-2-3-4-5-6-7: worst-case latency = max(500,700,800,900,1000,1100) = 1100.
    // Path 3: 0-2-7: worst-case latency = max(500,1500) = 1500.
    // The optimal worst-case latency is 1100.
    REQUIRE(result == 1100);
}