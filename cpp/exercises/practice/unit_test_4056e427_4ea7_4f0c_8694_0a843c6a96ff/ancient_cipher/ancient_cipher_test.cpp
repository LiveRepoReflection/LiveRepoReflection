#include "ancient_cipher.h"
#include <vector>
#include <tuple>
#include <limits>
#include <cassert>
#include <climits>
#include "catch.hpp"

using std::vector;
using std::tuple;
using std::make_tuple;
using std::pair;

TEST_CASE("Basic path exists") {
    int N = 4;
    vector<int> V = {1, 2, 3, 4};
    vector<tuple<int, int, int>> roads = {
        make_tuple(0, 1, 1),
        make_tuple(1, 2, 2),
        make_tuple(2, 3, 3),
        make_tuple(0, 2, -1)
    };
    int start_city = 0;
    int end_city = 3;
    int K = 3;
    
    pair<vector<int>, int> result = ancient_cipher::solve(N, V, roads, start_city, end_city, K);
    
    // Expected optimal path: [0, 2, 3] 
    vector<int> expected_path = {0, 2, 3};
    int expected_net = 6; // (1 + 3 + 4) - (-1 + 3) = 8 - 2 = 6
    REQUIRE(result.second == expected_net);
    REQUIRE(result.first == expected_path);
}

TEST_CASE("No path exists within K edges") {
    int N = 3;
    vector<int> V = {1, 1, 1};
    // There is a road from 0 to 1, but no road to reach 2.
    vector<tuple<int, int, int>> roads = { make_tuple(0, 1, 1) };
    int start_city = 0;
    int end_city = 2;
    int K = 2;
    
    pair<vector<int>, int> result = ancient_cipher::solve(N, V, roads, start_city, end_city, K);
    
    // Expect no valid path -> empty path and INT_MIN as value
    REQUIRE(result.first.empty());
    REQUIRE(result.second == INT_MIN);
}

TEST_CASE("Tie-break: Multiple optimal paths, choose one with fewer edges") {
    int N = 3;
    vector<int> V = {5, -1, 10};
    // Two possible paths:
    // Path1: [0, 2] => Value: 5+10=15, Cost: 10, Net = 5.
    // Path2: [0, 1, 2] => Value: 5 + (-1) + 10 = 14, Cost: (2+3)=5, Net = 9.
    vector<tuple<int, int, int>> roads = { make_tuple(0, 1, 2), make_tuple(1, 2, 3), make_tuple(0, 2, 10) };
    int start_city = 0;
    int end_city = 2;
    int K = 3;
    
    pair<vector<int>, int> result = ancient_cipher::solve(N, V, roads, start_city, end_city, K);
    
    vector<int> expected_path = {0, 1, 2};
    int expected_net = 9;
    REQUIRE(result.second == expected_net);
    REQUIRE(result.first == expected_path);
}

TEST_CASE("Cycle exploitation within K edges") {
    int N = 3;
    vector<int> V = {3, 0, 5};
    // Roads include a cycle between 0 and 1:
    // 0 -> 1 cost 1, 1 -> 0 cost -1, and finally 1 -> 2 cost 2.
    // One potential optimal path using cycles:
    // Path: [0, 1, 0, 1, 0, 1, 2]
    // Edge sequence: 0->1, 1->0, 0->1, 1->0, 0->1, 1->2  (6 edges)
    // City values: 3, 0, 3, 0, 3, 0, 5 => total = 14
    // Road costs: 1, -1, 1, -1, 1, 2 => total = 3
    // Net = 14 - 3 = 11
    vector<tuple<int, int, int>> roads = {
        make_tuple(0, 1, 1),
        make_tuple(1, 0, -1),
        make_tuple(1, 2, 2)
    };
    int start_city = 0;
    int end_city = 2;
    int K = 6;
    
    pair<vector<int>, int> result = ancient_cipher::solve(N, V, roads, start_city, end_city, K);
    
    vector<int> expected_path = {0, 1, 0, 1, 0, 1, 2};
    int expected_net = 11;
    REQUIRE(result.second == expected_net);
    REQUIRE(result.first == expected_path);
}

TEST_CASE("Edge case: Start equals end") {
    int N = 3;
    vector<int> V = {10, -5, 3};
    // Even if there are roads, the best path might be to not take any edges.
    vector<tuple<int, int, int>> roads = {
        make_tuple(0, 1, 2),
        make_tuple(1, 2, 3),
        make_tuple(2, 0, 4)
    };
    int start_city = 1;
    int end_city = 1;
    int K = 3;
    
    // In this case, the optimal path is just the single city [1] with net = V[1] = -5.
    pair<vector<int>, int> result = ancient_cipher::solve(N, V, roads, start_city, end_city, K);
    
    vector<int> expected_path = {1};
    int expected_net = -5;
    REQUIRE(result.second == expected_net);
    REQUIRE(result.first == expected_path);
}