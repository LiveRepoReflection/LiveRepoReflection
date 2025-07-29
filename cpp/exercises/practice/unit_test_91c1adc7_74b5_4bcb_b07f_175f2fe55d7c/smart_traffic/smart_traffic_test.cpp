#include "catch.hpp"
#include "smart_traffic.h"
#include <vector>
#include <tuple>

using std::vector;
using std::tuple;

TEST_CASE("Source equals sink") {
    int N = 1;
    int source = 0;
    int sink = 0;
    vector<tuple<int, int, int, int, int, int>> roads;
    // When source and sink are the same, no flow is needed.
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 0);
}

TEST_CASE("No path from source to sink") {
    int N = 3;
    int source = 0;
    int sink = 2;
    vector<tuple<int, int, int, int, int, int>> roads = {
        std::make_tuple(0, 1, 10, 0, 3, 100),
        std::make_tuple(1, 0, 5, 0, 0, 0)
    };
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 0);
}

TEST_CASE("Graph from example in description") {
    int N = 4;
    int source = 0;
    int sink = 3;
    vector<tuple<int, int, int, int, int, int>> roads = {
        std::make_tuple(0, 1, 10, 5, 5, 100),   // Road with toll booth: active effective = 0, disabled effective = 5, penalty = 100
        std::make_tuple(0, 2, 15, 7, 0, 0),       // No toll booth: effective = 8
        std::make_tuple(1, 2, 25, 10, 10, 50),     // Road with toll booth: active effective = 5, disabled effective = 15, penalty = 50
        std::make_tuple(1, 3, 10, 3, 5, 75),       // Road with toll booth: active effective = 2, disabled effective = 7, penalty = 75
        std::make_tuple(2, 3, 20, 8, 0, 0)         // No toll booth: effective = 12
    };
    // Optimal strategy avoids disabling toll booths because penalties are too high,
    // resulting in using only the toll-free path 0->2->3 with flow = min(8, 12) = 8.
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 8);
}

TEST_CASE("Graph with all toll-free roads") {
    int N = 4;
    int source = 0;
    int sink = 3;
    vector<tuple<int, int, int, int, int, int>> roads = {
        // Each toll booth cost is 0 meaning no toll present.
        std::make_tuple(0, 1, 10, 2, 0, 0),    // effective = 8
        std::make_tuple(1, 3, 10, 3, 0, 0),    // effective = 7
        std::make_tuple(0, 2, 5, 0, 0, 0),      // effective = 5
        std::make_tuple(2, 3, 15, 5, 0, 0)      // effective = 10
    };
    // Maximum flow can use two disjoint paths:
    // path1: 0->1->3 with flow = min(8,7) = 7;
    // path2: 0->2->3 with flow = min(5,10) = 5; total = 12.
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 12);
}

TEST_CASE("Graph with roads having zero capacity") {
    int N = 3;
    int source = 0;
    int sink = 2;
    vector<tuple<int, int, int, int, int, int>> roads = {
        std::make_tuple(0, 1, 5, 5, 5, 50),    // effective = 5 - 5 - 5 = -5 -> treated as 0
        std::make_tuple(1, 2, 7, 7, 0, 0)       // effective = 0
    };
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 0);
}

TEST_CASE("Mixed toll disabling decision scenario") {
    int N = 3;
    int source = 0;
    int sink = 2;
    vector<tuple<int, int, int, int, int, int>> roads = {
        // Road 0->1: active effective = 20-10-5 = 5, disabled effective = 10, penalty = 8
        std::make_tuple(0, 1, 20, 10, 5, 8),
        // Road 1->2: active effective = 15-5-2 = 8, disabled effective = 10, penalty = 3
        std::make_tuple(1, 2, 15, 5, 2, 3)
    };
    // Possible decisions:
    // - Use none: flow = min(5, 8) = 5, net = 5.
    // - Disable second only: flow = min(5,10)=5, net = 5 - 3 = 2.
    // - Disable first only: flow = min(10,8)=8, net = 8 - 8 = 0.
    // - Disable both: flow = min(10,10)=10, net = 10 - (8+3)= -1.
    // Thus the best is not to disable any, yielding 5.
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 5);
}

TEST_CASE("Graph with cycles and multiple roads between intersections") {
    int N = 5;
    int source = 0;
    int sink = 4;
    vector<tuple<int, int, int, int, int, int>> roads = {
        // Multiple paths with cycles
        std::make_tuple(0, 1, 15, 5, 3, 20),   // Road A: active = 15-5-3 = 7, disabled = 10, penalty = 20
        std::make_tuple(1, 2, 10, 3, 2, 10),   // Road B: active = 10-3-2 = 5, disabled = 7, penalty = 10
        std::make_tuple(2, 1, 5, 1, 1, 5),      // Road C (cycle): active = 5-1-1 = 3, disabled = 4, penalty = 5
        std::make_tuple(1, 3, 20, 10, 4, 30),   // Road D: active = 20-10-4 = 6, disabled = 10, penalty = 30
        std::make_tuple(3, 4, 25, 5, 0, 0),     // Road E: toll-free: effective = 20
        std::make_tuple(0, 2, 10, 2, 0, 0),     // Road F: toll-free: effective = 8
        std::make_tuple(2, 4, 10, 0, 0, 0)      // Road G: toll-free: effective = 10
    };
    // This complex graph demands the algorithm to account for cycles, multiple edges and toll booth effects.
    // The optimal strategy will decide on a combination of disabling tolls and using toll-free roads.
    // For this test case, assume the correct net maximum flow is 15.
    int result = smart_traffic::calculate_optimal_flow(N, source, sink, roads);
    REQUIRE(result == 15);
}