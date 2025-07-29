#include "drone_delivery.h"
#include "catch.hpp"

#include <tuple>
#include <vector>
#include <utility>

using namespace std;

TEST_CASE("Basic test case") {
    int N = 4;
    vector<tuple<int, int, int>> edges = {{0, 1, 10}, {0, 2, 15}, {1, 3, 12}, {2, 3, 8}};
    vector<pair<int, int>> time_windows = {{0, 30}, {20, 50}, {10, 40}, {0, 100}};
    vector<int> start_locations = {0};
    int target_location = 3;

    REQUIRE(23 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Multiple start locations") {
    int N = 5;
    vector<tuple<int, int, int>> edges = {
        {0, 2, 20}, {1, 2, 15}, {2, 3, 10}, {2, 4, 25}, {3, 4, 10}
    };
    vector<pair<int, int>> time_windows = {
        {0, 30}, {0, 50}, {20, 60}, {30, 70}, {40, 100}
    };
    vector<int> start_locations = {0, 1};
    int target_location = 4;

    REQUIRE(40 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Unreachable target") {
    int N = 3;
    vector<tuple<int, int, int>> edges = {{0, 1, 10}};
    vector<pair<int, int>> time_windows = {{0, 30}, {10, 50}, {20, 60}};
    vector<int> start_locations = {0};
    int target_location = 2;

    REQUIRE(-1 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Time window constraints") {
    int N = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 5}, {1, 3, 10}, {2, 3, 20}
    };
    vector<pair<int, int>> time_windows = {
        {0, 100}, {15, 25}, {10, 15}, {30, 50}
    };
    vector<int> start_locations = {0};
    int target_location = 3;

    // Path: 0->1->3, wait at 1 until 15, arrive at 3 at time 25
    REQUIRE(30 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Wait at intermediate locations") {
    int N = 5;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 5}, {0, 2, 10}, {1, 3, 15}, {2, 3, 10}, {3, 4, 5}
    };
    vector<pair<int, int>> time_windows = {
        {0, 100}, {10, 20}, {15, 25}, {30, 40}, {45, 55}
    };
    vector<int> start_locations = {0};
    int target_location = 4;

    // Path: 0->1->3->4, wait at 1 until 10, arrive at 3 at time 25, wait until 30, arrive at 4 at time 35
    REQUIRE(45 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Missed time window") {
    int N = 3;
    vector<tuple<int, int, int>> edges = {{0, 1, 30}, {1, 2, 10}};
    vector<pair<int, int>> time_windows = {{0, 100}, {10, 20}, {0, 50}};
    vector<int> start_locations = {0};
    int target_location = 2;

    // At location 1, drone arrives at time 30, which is after the time window [10, 20]
    REQUIRE(-1 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Complex graph with multiple paths") {
    int N = 6;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15}, {1, 2, 5}, {1, 3, 12}, 
        {2, 3, 8}, {2, 4, 10}, {3, 5, 20}, {4, 5, 15}
    };
    vector<pair<int, int>> time_windows = {
        {0, 30}, {10, 50}, {20, 40}, {30, 60}, {40, 70}, {50, 100}
    };
    vector<int> start_locations = {0};
    int target_location = 5;

    // Best path: 0->1->2->4->5, arriving at 5 at time 40
    REQUIRE(50 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Edge case: empty edges") {
    int N = 2;
    vector<tuple<int, int, int>> edges = {};
    vector<pair<int, int>> time_windows = {{0, 10}, {5, 15}};
    vector<int> start_locations = {0};
    int target_location = 1;

    REQUIRE(-1 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Edge case: target is a start location") {
    int N = 3;
    vector<tuple<int, int, int>> edges = {{0, 1, 10}, {1, 2, 15}};
    vector<pair<int, int>> time_windows = {{5, 30}, {20, 50}, {30, 60}};
    vector<int> start_locations = {0, 2};
    int target_location = 2;

    // Since 2 is already a start location, the earliest arrival time is its time window start
    REQUIRE(30 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}

TEST_CASE("Multiple equal-length paths with different wait times") {
    int N = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 5}, {1, 3, 15}, {2, 3, 20}
    };
    vector<pair<int, int>> time_windows = {
        {0, 100}, {10, 20}, {5, 10}, {25, 40}
    };
    vector<int> start_locations = {0};
    int target_location = 3;

    // Path 1: 0->1->3, arrive at 1 at time 10, leave at 10, arrive at 3 at time 25
    // Path 2: 0->2->3, arrive at 2 at time 5, leave at 5, arrive at 3 at time 25
    // Both paths result in arrival at time 25, but Path 1 allows for an earlier delivery start
    REQUIRE(25 == drone_delivery::find_earliest_arrival_time(N, edges, time_windows, start_locations, target_location));
}