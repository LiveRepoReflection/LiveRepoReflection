#include <vector>
#include <string>
#include "catch.hpp"
#include "vehicle_routing.h"

using namespace std;

// Test Case 1: Basic Route - Static grid with no dynamic obstacles
TEST_CASE("basic_route_static") {
    int N = 3;
    int F = 10;
    int K = 0;
    // Only one configuration provided.
    vector<vector<string>> configurations = {
        {
            "S..",
            "...",
            "..D"
        }
    };
    // Minimal Manhattan distance from (0,0) to (2,2) is 4 moves.
    // Expected answer: 4
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == 4);
}

// Test Case 2: Dynamic Obstacle Route - Grid with two configurations forcing detour
TEST_CASE("dynamic_obstacle_route") {
    int N = 3;
    int F = 10;
    int K = 0;
    // Two configurations: initial and one update.
    vector<vector<string>> configurations = {
        {   // Configuration 0
            "S#.",
            "...",
            "..D"
        },
        {   // Configuration 1 (remains for t >= 1)
            "S..",
            ".#.",
            "..D"
        }
    };
    // Expected optimal route:
    // t=0 (config0): at S(0,0) can only move down to (1,0) because right is blocked.
    // t=1 (config1): from (1,0), proceed: (1,0)->(2,0)->(2,1)->(2,2).
    // Total moves = 4.
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == 4);
}

// Test Case 3: Unreachable due to Obstacles - No valid route exists
TEST_CASE("unreachable_due_to_obstacles") {
    int N = 3;
    int F = 10;
    int K = 0;
    vector<vector<string>> configurations = {
        {
            "S##",
            "###",
            "##D"
        },
        {
            "S##",
            "###",
            "##D"
        }
    };
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == -1);
}

// Test Case 4: Fuel Constraint Failure - Fuel capacity too small to reach destination
TEST_CASE("fuel_constraint_failure") {
    int N = 3;
    int F = 3;  // Fuel capacity less than Manhattan distance of 4
    int K = 0;
    vector<vector<string>> configurations = {
        {
            "S..",
            "...",
            "..D"
        }
    };
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == -1);
}

// Test Case 5: Charging Station Usage - Route requires stopping at a charging station
TEST_CASE("charging_station_usage") {
    int N = 4;
    int F = 5;  // Fuel capacity is limited (5 moves)
    int K = 1;  // Can visit at most one charging station
    vector<vector<string>> configurations = {
        {
            "S...",
            ".C..",
            "....",
            "...D"
        }
    };
    // One optimal route:
    // (0,0) -> (0,1) -> (1,1) [charging station reached, fuel refilled],
    // then (1,1) -> (1,2) -> (2,2) -> (2,3) -> (3,3).
    // Total moves = 2 (to charge) + 4 = 6.
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == 6);
}

// Test Case 6: Dynamic Obstacles with Charging - Combines dynamic obstacles and fuel constraints requiring a charge
TEST_CASE("dynamic_and_charging") {
    int N = 4;
    int F = 4;  // Lower fuel capacity necessitates charging
    int K = 1;  // Only one charging station visit allowed
    // Fixed positions: S at (0,0), charging station C at (2,0), destination D at (3,3) (remains constant).
    vector<vector<string>> configurations = {
        {   // Configuration 0
            "S...",
            ".##.",
            "C.#.",
            "...D"
        },
        {   // Configuration 1 (applied at t>=1)
            "S...",
            "....",
            "C..#",
            ".#.D"
        }
    };
    // One possible route:
    // t=0 (config0): from S(0,0), move down to (1,0). (Fuel: 4->3)
    // t=1 (config1): from (1,0) move down to (2,0) where charging station is located.
    //   Fuel is refilled to 4, and one charge is used.
    // Then from (2,0) in config1:
    // (2,0) -> (2,1) -> (2,2) -> (3,2) -> (3,3)
    // Total moves = 1 (to (1,0)) + 1 (to (2,0)) + 4 (to destination) = 6.
    int result = vehicle_routing::solve(N, F, K, configurations.size(), configurations);
    REQUIRE(result == 6);
}