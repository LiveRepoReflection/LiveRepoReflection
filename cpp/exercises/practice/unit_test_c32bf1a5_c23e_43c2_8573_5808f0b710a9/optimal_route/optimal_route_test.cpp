#include "catch.hpp"
#include "optimal_route.h"
#include <vector>
#include <tuple>

TEST_CASE("Simple route with two customers") {
    int num_intersections = 4;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15}, {0, 3, 20},
        {1, 0, 10}, {1, 2, 5}, {1, 3, 12},
        {2, 0, 10}, {2, 1, 5}, {2, 3, 8},
        {3, 0, 15}, {3, 1, 12}, {3, 2, 8}
    };
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2};
    int max_route_time = 50;

    REQUIRE(25 == optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time));
}

TEST_CASE("Route with three customers") {
    int num_intersections = 5;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15}, {0, 3, 20}, {0, 4, 25},
        {1, 0, 10}, {1, 2, 5}, {1, 3, 12}, {1, 4, 18},
        {2, 0, 15}, {2, 1, 5}, {2, 3, 8}, {2, 4, 15},
        {3, 0, 20}, {3, 1, 12}, {3, 2, 8}, {3, 4, 10},
        {4, 0, 25}, {4, 1, 18}, {4, 2, 15}, {4, 3, 10}
    };
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2, 3};
    int max_route_time = 50;

    REQUIRE(43 == optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time));
}

TEST_CASE("No valid route under time constraint") {
    int num_intersections = 4;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15}, {0, 3, 20},
        {1, 0, 10}, {1, 2, 5}, {1, 3, 12},
        {2, 0, 10}, {2, 1, 5}, {2, 3, 8},
        {3, 0, 15}, {3, 1, 12}, {3, 2, 8}
    };
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2, 3};
    int max_route_time = 30;  // Not enough time to visit all customers and return

    REQUIRE(-1 == optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time));
}

TEST_CASE("Only one customer") {
    int num_intersections = 3;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15},
        {1, 0, 10}, {1, 2, 7},
        {2, 0, 15}, {2, 1, 7}
    };
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1};
    int max_route_time = 25;

    REQUIRE(20 == optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time));
}

TEST_CASE("Maximum number of customers") {
    int num_intersections = 6;
    std::vector<std::tuple<int, int, int>> edges;
    
    // Create a fully connected graph
    for (int i = 0; i < num_intersections; i++) {
        for (int j = 0; j < num_intersections; j++) {
            if (i != j) {
                edges.push_back({i, j, 5 + (i * j % 5)});  // Varied weights
            }
        }
    }
    
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2, 3, 4, 5};
    int max_route_time = 100;

    // The exact value depends on edge weights, but there should be a valid solution
    int result = optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time);
    
    REQUIRE(result > 0);
    REQUIRE(result <= max_route_time);
}

TEST_CASE("All possible edges with varied weights") {
    int num_intersections = 5;
    std::vector<std::tuple<int, int, int>> edges;
    
    // Create all possible edges with varied weights
    for (int i = 0; i < num_intersections; i++) {
        for (int j = 0; j < num_intersections; j++) {
            if (i != j) {
                int weight = (i + 1) * (j + 1) % 15 + 5;  // Creates diverse weights
                edges.push_back({i, j, weight});
            }
        }
    }
    
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2, 3, 4};
    int max_route_time = 100;

    int result = optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time);
    
    REQUIRE(result > 0);
    REQUIRE(result <= max_route_time);
}

TEST_CASE("Edge case: Max time exactly matches optimal route") {
    int num_intersections = 4;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10}, {0, 2, 15}, {0, 3, 20},
        {1, 0, 10}, {1, 2, 5}, {1, 3, 12},
        {2, 0, 10}, {2, 1, 5}, {2, 3, 8},
        {3, 0, 15}, {3, 1, 12}, {3, 2, 8}
    };
    int depot_intersection = 0;
    std::vector<int> customer_intersections = {1, 2};
    int max_route_time = 25;  // Exactly the time needed for optimal route

    REQUIRE(25 == optimal_route::min_travel_time(
        num_intersections, edges, depot_intersection, 
        customer_intersections, max_route_time));
}