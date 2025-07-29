#include "optimal_traffic.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using namespace std;

TEST_CASE("Basic direct route") {
    int num_intersections = 2;
    // Each road is represented as: (source, destination, initial_capacity, travel_time)
    vector<tuple<int, int, int, int>> roads = {
        make_tuple(0, 1, 5, 3)
    };
    vector<int> start_intersections = {0};
    int destination = 1;
    // No capacity updates
    vector<tuple<int, int, int, int, int>> capacity_updates;
    
    // Expected: one car travels from 0 -> 1, taking time 3.
    int expected = 3;
    int result = optimal_traffic::earliest_arrival(num_intersections, roads, start_intersections, destination, capacity_updates);
    REQUIRE(result == expected);
}

TEST_CASE("Multiple cars with capacity bottleneck") {
    int num_intersections = 3;
    // Define two roads:
    // Road from 0 -> 1 with capacity 1 and travel time 1.
    // Road from 1 -> 2 with capacity 2 and travel time 2.
    vector<tuple<int, int, int, int>> roads = {
        make_tuple(0, 1, 1, 1),
        make_tuple(1, 2, 2, 2)
    };
    // Two cars starting at intersection 0.
    vector<int> start_intersections = {0, 0};
    int destination = 2;
    vector<tuple<int, int, int, int, int>> capacity_updates;
    
    // Expected simulation:
    // First car: enters road (0,1) at time 0, reaches intersection 1 at time 1, enters road (1,2) at time 1, arrives at destination at time 3.
    // Second car: waits at intersection 0 until time 1, then enters road (0,1) at time 1, reaches intersection 1 at time 2, enters road (1,2) at time 2, arrives at destination at time 4.
    // Therefore, all cars have arrived by time 4.
    int expected = 4;
    int result = optimal_traffic::earliest_arrival(num_intersections, roads, start_intersections, destination, capacity_updates);
    REQUIRE(result == expected);
}

TEST_CASE("Dynamic capacity update test") {
    int num_intersections = 4;
    // Roads: (source, destination, initial_capacity, travel_time)
    vector<tuple<int, int, int, int>> roads = {
        make_tuple(0, 1, 2, 1),
        make_tuple(1, 2, 1, 2),
        make_tuple(0, 2, 1, 3),
        make_tuple(2, 3, 2, 1)
    };
    // Two cars starting at intersection 0.
    vector<int> start_intersections = {0, 0};
    int destination = 3;
    // Capacity update: Road from 1->2 will have capacity increased from 1 to 2 during time range 1 to 3.
    vector<tuple<int, int, int, int, int>> capacity_updates = {
        make_tuple(1, 2, 1, 3, 2)
    };
    
    // Expected simulation:
    // One possible optimal schedule is:
    // Car 1: 0->1 at time 0 (arrives at 1 at time 1), then 1->2 at time 1 (arrives at 2 at time 3), then 2->3 at time 3 (arrives at 3 at time 4).
    // Car 2: 0->1 at time 0 (possible since capacity of road 0->1 is 2) and arrives at 1 at time 1, then must wait if both cannot enter (depending on capacity constraints)
    // Alternatively, Car 2 may take road 0->2 directly at time 0 (arriving at 2 at time 3) then 2->3 at time 3 (arriving at 3 at time 4).
    // In any optimal scheduling, both cars can be arranged to reach intersection 3 by time 4.
    int expected = 4;
    int result = optimal_traffic::earliest_arrival(num_intersections, roads, start_intersections, destination, capacity_updates);
    REQUIRE(result == expected);
}

TEST_CASE("Impossible route") {
    int num_intersections = 3;
    // Only one road from 0->1 is available.
    vector<tuple<int, int, int, int>> roads = {
        make_tuple(0, 1, 2, 1)
    };
    // Car starting at 0, but destination is 2 which is unreachable.
    vector<int> start_intersections = {0};
    int destination = 2;
    vector<tuple<int, int, int, int, int>> capacity_updates;
    
    int expected = -1;
    int result = optimal_traffic::earliest_arrival(num_intersections, roads, start_intersections, destination, capacity_updates);
    REQUIRE(result == expected);
}