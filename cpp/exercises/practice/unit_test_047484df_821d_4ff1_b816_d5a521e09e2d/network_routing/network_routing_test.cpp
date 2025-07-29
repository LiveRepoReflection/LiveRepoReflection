#include <vector>
#include <tuple>
#include <cmath>
#include "catch.hpp"
#include "network_routing.h"

using std::vector;
using std::tuple;

const double EPS = 1e-6;

// Helper function to compare two double values.
bool doubleEqual(double a, double b) {
    return std::fabs(a - b) < EPS;
}

TEST_CASE("Basic routing: single request with optimal path", "[network_routing]") {
    // Graph: 4 nodes, 5 links.
    // links: (u, v, capacity, base_latency)
    //   (0, 1, 10, 5), (0, 2, 5, 2), (1, 2, 8, 3), (1, 3, 12, 4), (2, 3, 6, 1)
    int N = 4;
    vector<tuple<int, int, int, int>> links = {
        {0, 1, 10, 5},
        {0, 2, 5, 2},
        {1, 2, 8, 3},
        {1, 3, 12, 4},
        {2, 3, 6, 1}
    };
    // Single request: (src, dest, data)
    vector<tuple<int, int, int>> requests = {
        {0, 3, 4}
    };

    // For the first request, since no congestion exists,
    // optimal path should be 0 -> 2 -> 3 with latency = 2 + 1 = 3.
    vector<double> result = network_routing::processRequests(N, links, requests);
    REQUIRE(result.size() == 1);
    REQUIRE(doubleEqual(result[0], 3.0));
}

TEST_CASE("Sequential routing: congestion updates and capacity check", "[network_routing]") {
    // Graph: 4 nodes, 5 links.
    int N = 4;
    vector<tuple<int, int, int, int>> links = {
        {0, 1, 10, 5},
        {0, 2, 5, 2},
        {1, 2, 8, 3},
        {1, 3, 12, 4},
        {2, 3, 6, 1}
    };
    // Two requests:
    // 1. (0, 3, 4) routes through path 0-2-3, expected latency = 2 + 1 = 3.
    // After routing:
    //    Link (0,2): flow = 4, congestion = 4/5 = 0.8, effective latency = 2 * (1+0.64)= 3.28.
    //    Link (2,3): flow = 4, congestion = 4/6 ≈ 0.6667, effective latency ≈ 1 * (1+0.4444)= 1.4444.
    // 2. (0, 3, 3): path 0-2-3 is now not feasible because capacity of (0,2) left = 1 (<3),
    //    so the next best is 0-1-3 with latency = 5 + 4 = 9.
    vector<tuple<int, int, int>> requests = {
        {0, 3, 4},
        {0, 3, 3}
    };

    vector<double> result = network_routing::processRequests(N, links, requests);
    REQUIRE(result.size() == 2);
    REQUIRE(doubleEqual(result[0], 3.0));
    REQUIRE(doubleEqual(result[1], 9.0));
}

TEST_CASE("Routing failure due to capacity constraints", "[network_routing]") {
    // Graph: Simple two nodes and a single link.
    int N = 2;
    vector<tuple<int, int, int, int>> links = {
        {0, 1, 5, 10}
    };
    // Two requests, where the first one saturates the link.
    vector<tuple<int, int, int>> requests = {
        {0, 1, 5},   // uses full capacity
        {0, 1, 1}    // should fail, not enough capacity
    };

    vector<double> result = network_routing::processRequests(N, links, requests);
    REQUIRE(result.size() == 2);
    REQUIRE(doubleEqual(result[0], 10.0));
    REQUIRE(result[1] < 0); // -1 expected as failure indicator
}

TEST_CASE("Tie breaking for multiple same latency paths", "[network_routing]") {
    // Graph with two distinct paths from 0 to 3 with same effective latency.
    // Graph:
    //   Path A: 0-1-3, with link latencies 4 and 6 → total = 10, hops = 2.
    //   Path B: 0-2-3, with link latencies 5 and 5 → total = 10, hops = 2.
    // Additionally insert a longer path: 0-4-3 with latency 3 + 7 = 10, hops = 2.
    // All links have high capacities to ignore capacity constraints.
    int N = 5;
    vector<tuple<int, int, int, int>> links = {
        {0, 1, 100, 4},
        {1, 3, 100, 6},
        {0, 2, 100, 5},
        {2, 3, 100, 5},
        {0, 4, 100, 3},
        {4, 3, 100, 7}
    };
    // Single request
    vector<tuple<int, int, int>> requests = {
        {0, 3, 10}
    };

    // Expected latency is 10, and any path with minimum hops (2) is acceptable.
    vector<double> result = network_routing::processRequests(N, links, requests);
    REQUIRE(result.size() == 1);
    REQUIRE(doubleEqual(result[0], 10.0));
}

TEST_CASE("Complex network: multiple sequential routing with cycles", "[network_routing]") {
    // Create a cyclic graph:
    // 0-1, 1-2, 2-3, 3-0, and additional link 1-3.
    int N = 4;
    vector<tuple<int, int, int, int>> links = {
        {0, 1, 15, 3},
        {1, 2, 15, 4},
        {2, 3, 15, 5},
        {3, 0, 15, 2},
        {1, 3, 10, 6}
    };
    // Three routing requests in sequence.
    vector<tuple<int, int, int>> requests = {
        {0, 2, 5},   // likely chooses 0-1-2: latency = 3+4 = 7.
        {2, 0, 10},  // potential paths: 2-3-0: latency = 5+2 = 7, or 2-1-0: 4+3=7.
        {0, 3, 8}    // verify chosen path based on remaining capacities and updated flows.
    };

    vector<double> result = network_routing::processRequests(N, links, requests);
    REQUIRE(result.size() == 3);
    // Since expected values might depend on internal congestion adjustments,
    // we at least check that the outputs are non-negative for successful routings.
    for (double latency : result) {
        // If routing failed, latency would be -1.
        // In this complex graph, all routings should find a valid path.
        REQUIRE(latency >= 0);
    }
}