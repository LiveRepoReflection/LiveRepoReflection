#include "delivery_network.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using std::vector;
using std::tuple;

TEST_CASE("Single city - no delivery cost", "[delivery_network]") {
    int num_cities = 1;
    vector<tuple<int, int, int, int>> roads; // no roads needed
    double distance_weight = 1.0;
    double toll_weight = 1.0;
    double expected_cost = 0.0;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}

TEST_CASE("Two cities - single road", "[delivery_network]") {
    int num_cities = 2;
    // Road: city0 - city1 with distance=10, toll=5
    // Total cost = 10*1.0 + 5*2.0 = 10 + 10 = 20
    vector<tuple<int, int, int, int>> roads = {
        {0, 1, 10, 5}
    };
    double distance_weight = 1.0;
    double toll_weight = 2.0;
    double expected_cost = 20.0;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}

TEST_CASE("Triangle graph - three cities", "[delivery_network]") {
    int num_cities = 3;
    // Cities: 0,1,2
    // Roads:
    // (0,1): distance=4, toll=1 => cost = 4*2.0 + 1*1.0 = 8+1=9
    // (1,2): distance=2, toll=3 => cost = 2*2.0 + 3*1.0 = 4+3=7
    // (0,2): distance=3, toll=2 => cost = 3*2.0 + 2*1.0 = 6+2=8
    // MST should choose edges (0,2) and (1,2): 8 + 7 = 15
    vector<tuple<int, int, int, int>> roads = {
        {0, 1, 4, 1},
        {1, 2, 2, 3},
        {0, 2, 3, 2}
    };
    double distance_weight = 2.0;
    double toll_weight = 1.0;
    double expected_cost = 15.0;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}

TEST_CASE("Four cities - multiple paths", "[delivery_network]") {
    int num_cities = 4;
    // Cities: 0,1,2,3
    // Roads:
    // (0,1): d=1, toll=10 => 1+10 = 11  (using weights dw=1, tw=1)
    // (0,2): d=2, toll=2  => 2+2 = 4
    // (1,2): d=1, toll=1  => 1+1 = 2
    // (1,3): d=10, toll=1 => 10+1 = 11
    // (2,3): d=2, toll=8  => 2+8 = 10
    // MST should pick the edges (1,2):2, (0,2):4, (2,3):10 => total = 16
    vector<tuple<int, int, int, int>> roads = {
        {0, 1, 1, 10},
        {0, 2, 2, 2},
        {1, 2, 1, 1},
        {1, 3, 10, 1},
        {2, 3, 2, 8}
    };
    double distance_weight = 1.0;
    double toll_weight = 1.0;
    double expected_cost = 16.0;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}

TEST_CASE("Non-integer weighted costs", "[delivery_network]") {
    int num_cities = 3;
    // Cities: 0, 1, 2
    // Roads:
    // (0,1): d=5, toll=5 => cost = 5*1.5 + 5*2.5 = 7.5+12.5 = 20.0
    // (1,2): d=3, toll=10 => cost = 3*1.5 + 10*2.5 = 4.5+25 = 29.5
    // (0,2): d=8, toll=1 => cost = 8*1.5 + 1*2.5 = 12+2.5 = 14.5
    // MST should pick (0,1) and (0,2) => 20.0 + 14.5 = 34.5
    vector<tuple<int, int, int, int>> roads = {
        {0, 1, 5, 5},
        {1, 2, 3, 10},
        {0, 2, 8, 1}
    };
    double distance_weight = 1.5;
    double toll_weight = 2.5;
    double expected_cost = 34.5;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}

TEST_CASE("Star graph with extra edge for optimization", "[delivery_network]") {
    int num_cities = 5;
    // Cities: 0,1,2,3,4 (0 is the center)
    // Roads from center:
    // (0,1): d=3, toll=5 => cost = 3*2 + 5*1 = 6+5 = 11
    // (0,2): d=4, toll=1 => cost = 4*2 + 1*1 = 8+1 = 9
    // (0,3): d=2, toll=4 => cost = 2*2 + 4*1 = 4+4 = 8
    // (0,4): d=1, toll=10 => cost = 1*2 + 10*1 = 2+10 = 12
    // Extra road:
    // (3,4): d=1, toll=1 => cost = 1*2 + 1*1 = 2+1 = 3
    // MST should select:
    // (0,3): 8, (3,4): 3, (0,2): 9, (0,1): 11 => total = 8+3+9+11 = 31
    vector<tuple<int, int, int, int>> roads = {
        {0, 1, 3, 5},
        {0, 2, 4, 1},
        {0, 3, 2, 4},
        {0, 4, 1, 10},
        {3, 4, 1, 1}
    };
    double distance_weight = 2.0;
    double toll_weight = 1.0;
    double expected_cost = 31.0;
    double result = delivery_network::computeOptimalCost(num_cities, roads, distance_weight, toll_weight);
    CHECK(result == Approx(expected_cost));
}