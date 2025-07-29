#include "network_optimize.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using namespace std;

TEST_CASE("Single city", "[network_optimize]") {
    int n = 1;
    vector<int> b = {12};
    vector<tuple<int, int, long long>> roads; // no roads for single city

    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == 0);
}

TEST_CASE("Disconnected graph", "[network_optimize]") {
    int n = 2;
    vector<int> b = {5, 10};
    vector<tuple<int, int, long long>> roads; // no roads, graph is disconnected

    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == -1);
}

TEST_CASE("Two cities with one road", "[network_optimize]") {
    int n = 2;
    vector<int> b = {5, 10};
    vector<tuple<int, int, long long>> roads = {
        {0, 1, 7}
    };
    // Cost: max(5,10) * 7 = 10 * 7 = 70
    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == 70);
}

TEST_CASE("Four cities test", "[network_optimize]") {
    int n = 4;
    vector<int> b = {10, 15, 5, 20};
    vector<tuple<int, int, long long>> roads = {
        {0, 1, 10},
        {0, 2, 5},
        {1, 2, 8},
        {1, 3, 12},
        {2, 3, 15}
    };
    // Expected MST (by optimal selection):
    // Edge 0-2: cost = max(10, 5) * 5 = 10 * 5 = 50
    // Edge 1-2: cost = max(15, 5) * 8 = 15 * 8 = 120
    // Edge 1-3: cost = max(15, 20) * 12 = 20 * 12 = 240
    // Total = 50 + 120 + 240 = 410
    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == 410);
}

TEST_CASE("Five cities complex", "[network_optimize]") {
    int n = 5;
    vector<int> b = {5, 7, 3, 10, 8};
    vector<tuple<int, int, long long>> roads = {
        {0, 1, 2},
        {1, 2, 3},
        {2, 3, 4},
        {3, 4, 1},
        {0, 4, 10},
        {1, 3, 5}
    };
    // A potential optimal network:
    // Edge (0,1): cost = max(5,7) * 2 = 7 * 2 = 14
    // Edge (1,2): cost = max(7,3) * 3 = 7 * 3 = 21
    // Edge (2,3): cost = max(3,10) * 4 = 10 * 4 = 40
    // Edge (3,4): cost = max(10,8) * 1 = 10 * 1 = 10
    // Total = 14 + 21 + 40 + 10 = 85
    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == 85);
}

TEST_CASE("Multiple roads between same nodes", "[network_optimize]") {
    int n = 3;
    vector<int> b = {5, 9, 4};
    vector<tuple<int, int, long long>> roads = {
        {0, 1, 5},
        {0, 1, 3},
        {1, 2, 4},
        {0, 2, 10}
    };
    // For the edge (0,1), the optimal choice is the road with distance 3:
    // Cost for (0,1): max(5,9) * 3 = 9 * 3 = 27
    // For (1,2): cost = max(9,4) * 4 = 9 * 4 = 36
    // MST Total = 27 + 36 = 63
    long long result = network_optimize::compute_minimum_cost(n, b, roads);
    REQUIRE(result == 63);
}