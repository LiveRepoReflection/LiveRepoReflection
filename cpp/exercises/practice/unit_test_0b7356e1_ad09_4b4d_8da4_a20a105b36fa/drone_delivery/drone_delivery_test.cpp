#include "drone_delivery.h"
#include <vector>
#include <utility>
#include <algorithm>
#include <unordered_set>
#include "catch.hpp"

using namespace std;

// Helper function to compare two vectors irrespective of order.
bool compareUnordered(const vector<int>& result, const vector<int>& expected) {
    unordered_set<int> resSet(result.begin(), result.end());
    unordered_set<int> expSet(expected.begin(), expected.end());
    return resSet == expSet;
}

TEST_CASE("Single delivery feasible") {
    // Graph: 2 nodes. 0: depot, 1: delivery point.
    // Edge: 0->1 cost 5, 1->0 cost 5.
    int num_nodes = 2;
    vector<vector<pair<int, int>>> adjacency_list(num_nodes);
    adjacency_list[0].push_back({1, 5});
    adjacency_list[1].push_back({0, 5});
    
    // One delivery: id=1, destination=1, weight=1, deadline=10 (one-way travel time = 5)
    vector<vector<int>> delivery_requests = { {1, 1, 1, 10} };
    
    int drone_capacity = 2;
    // Drone flight time must cover round-trip: 5 + 5 = 10.
    int drone_flight_time = 10;
    
    vector<int> result = schedule_deliveries(num_nodes, adjacency_list, delivery_requests, drone_capacity, drone_flight_time);
    vector<int> expected = { 1 };
    
    REQUIRE(compareUnordered(result, expected));
}

TEST_CASE("Delivery fails due to insufficient flight time") {
    // Graph: 2 nodes. 0: depot, 1: delivery point.
    // Edge: 0->1 cost 7, 1->0 cost 7.
    int num_nodes = 2;
    vector<vector<pair<int, int>>> adjacency_list(num_nodes);
    adjacency_list[0].push_back({1, 7});
    adjacency_list[1].push_back({0, 7});
    
    // One delivery: id=10, destination=1, weight=1, deadline=10 (one-way travel time = 7, but round trip = 14)
    vector<vector<int>> delivery_requests = { {10, 1, 1, 10} };
    
    int drone_capacity = 2;
    // Drone flight time less than round-trip.
    int drone_flight_time = 12;
    
    vector<int> result = schedule_deliveries(num_nodes, adjacency_list, delivery_requests, drone_capacity, drone_flight_time);
    vector<int> expected = { };  // Not deliverable due to battery constraint.
    
    REQUIRE(compareUnordered(result, expected));
}

TEST_CASE("Delivery fails due to overweight package") {
    // Graph: 2 nodes. 0: depot, 1: delivery point.
    int num_nodes = 2;
    vector<vector<pair<int, int>>> adjacency_list(num_nodes);
    adjacency_list[0].push_back({1, 4});
    adjacency_list[1].push_back({0, 4});
    
    // One delivery: id=20, destination=1, weight=5, deadline=10 (one-way = 4, round-trip = 8)
    vector<vector<int>> delivery_requests = { {20, 1, 5, 10} };
    
    // Drone capacity is less
    int drone_capacity = 3;
    int drone_flight_time = 10;
    
    vector<int> result = schedule_deliveries(num_nodes, adjacency_list, delivery_requests, drone_capacity, drone_flight_time);
    vector<int> expected = { };  // Not deliverable due to overweight.
    
    REQUIRE(compareUnordered(result, expected));
}

TEST_CASE("Multiple deliveries with mixed feasibility") {
    // Graph: 4 nodes. Nodes: 0-depot, 1, 2, 3-delivery points.
    // Edges: 
    // 0 <-> 1: 2 minutes, 1 <-> 2: 3 minutes, 2 <-> 3: 4 minutes, 0 <-> 2: 5 minutes, 1 <-> 3: 6 minutes.
    int num_nodes = 4;
    vector<vector<pair<int, int>>> adjacency_list(num_nodes);
    // Bidirectional edges
    adjacency_list[0].push_back({1, 2});
    adjacency_list[1].push_back({0, 2});
    adjacency_list[1].push_back({2, 3});
    adjacency_list[2].push_back({1, 3});
    adjacency_list[2].push_back({3, 4});
    adjacency_list[3].push_back({2, 4});
    adjacency_list[0].push_back({2, 5});
    adjacency_list[2].push_back({0, 5});
    adjacency_list[1].push_back({3, 6});
    adjacency_list[3].push_back({1, 6});
    
    // Delivery requests:
    // id 101: destination=1, weight=1, deadline=8. One-way minimal = 2.
    // id 102: destination=2, weight=1, deadline=12. One-way minimal = 2+3=5 (via 0->1->2) or direct 5.
    // id 103: destination=3, weight=1, deadline=20. One-way minimal = 2+3+4=9.
    // id 104: destination=3, weight=1, deadline=7. Deadline too tight.
    vector<vector<int>> delivery_requests = {
        {101, 1, 1, 8},
        {102, 2, 1, 12},
        {103, 3, 1, 20},
        {104, 3, 1, 7}
    };
    
    int drone_capacity = 1;
    // Drone flight time must allow round-trip for all that are deliverable.
    // For destination 3, round-trip minimal = 9 + 9 = 18.
    int drone_flight_time = 20;
    
    vector<int> result = schedule_deliveries(num_nodes, adjacency_list, delivery_requests, drone_capacity, drone_flight_time);
    // Expected deliveries: 101, 102, 103 are deliverable.
    vector<int> expected = { 101, 102, 103 };
    
    REQUIRE(compareUnordered(result, expected));
}

TEST_CASE("Delivery fails due to missed deadline") {
    // Graph: 2 nodes. 0: depot, 1: delivery point.
    // Edge: 0->1: 4 minutes, 1->0: 4 minutes.
    int num_nodes = 2;
    vector<vector<pair<int, int>>> adjacency_list(num_nodes);
    adjacency_list[0].push_back({1, 4});
    adjacency_list[1].push_back({0, 4});
    
    // Delivery request: id=301, destination=1, weight=1, deadline=6 minutes.
    // One-way travel time is 4, so it reaches at 4 minutes, which is within deadline.
    // Then add a delivery with a stricter deadline.
    vector<vector<int>> delivery_requests = {
        {301, 1, 1, 6},  // Feasible
        {302, 1, 1, 3}   // Misses deadline because 4 > 3
    };
    
    int drone_capacity = 2;
    int drone_flight_time = 10;
    
    vector<int> result = schedule_deliveries(num_nodes, adjacency_list, delivery_requests, drone_capacity, drone_flight_time);
    // Only delivery 301 is feasible on time.
    vector<int> expected = { 301 };
    
    REQUIRE(compareUnordered(result, expected));
}