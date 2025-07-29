#include <vector>
#include <stdexcept>
#include <string>
#include "catch.hpp"
#include "drone_delivery.h"

using namespace drone_delivery;

TEST_CASE("Plan route finds valid route in a simple graph", "[drone_delivery]") {
    // Create a simple graph with intersections: 0, 1, 2
    // Streets: 0->1 (travel time 10, capacity 2), 1->2 (travel time 10, capacity 2)
    std::vector<Street> streets = {
        {0, 1, 10, 2},
        {1, 2, 10, 2}
    };
    // List of intersections (not used directly but might be part of system initialization)
    std::vector<int> intersections = {0, 1, 2};

    // Initialize the drone delivery system
    DroneDeliverySystem system(intersections, streets);

    // Create a delivery request with ample deadline
    DeliveryRequest request;
    request.start_intersection = 0;
    request.destination_intersection = 2;
    request.deadline = 100;  // sufficient deadline
    request.priority = 5;
    request.arrival_time = 0;

    std::vector<int> route = system.plan_route(request);
    // Expected route is 0 -> 1 -> 2
    std::vector<int> expected_route = {0, 1, 2};

    REQUIRE(route == expected_route);
}

TEST_CASE("Plan route returns no route if deadline is too short", "[drone_delivery]") {
    // Graph: 0->1 (10 sec) and 1->2 (10 sec)
    std::vector<Street> streets = {
        {0, 1, 10, 2},
        {1, 2, 10, 2}
    };
    std::vector<int> intersections = {0, 1, 2};

    DroneDeliverySystem system(intersections, streets);

    // Deadline is shorter than the needed 20 seconds
    DeliveryRequest request;
    request.start_intersection = 0;
    request.destination_intersection = 2;
    request.deadline = 15;  // too short
    request.priority = 5;
    request.arrival_time = 0;

    std::vector<int> route = system.plan_route(request);
    // Expect empty vector to indicate "No Route Possible"
    REQUIRE(route.empty());
}

TEST_CASE("Plan route returns no route when capacity constraint is violated", "[drone_delivery]") {
    // Graph with one street that has zero capacity.
    std::vector<Street> streets = {
        {0, 1, 10, 0}  // street cannot handle any drone
    };
    std::vector<int> intersections = {0, 1};

    DroneDeliverySystem system(intersections, streets);

    DeliveryRequest request;
    request.start_intersection = 0;
    request.destination_intersection = 1;
    request.deadline = 100;
    request.priority = 7;
    request.arrival_time = 0;

    std::vector<int> route = system.plan_route(request);
    // Expect no route because the only available street cannot be used
    REQUIRE(route.empty());
}

TEST_CASE("Plan route selects faster available route when meeting constraints", "[drone_delivery]") {
    // Create a graph with intersections: 0, 1, 2, 3
    // Two possible routes from 0 to 2:
    // Route A: 0 -> 1 -> 2, travel time 10 + 10 = 20, capacity 2 on each street.
    // Route B: 0 -> 3 -> 2, travel time 5 + 5 = 10, capacity 1 on each street.
    std::vector<Street> streets = {
        {0, 1, 10, 2},
        {1, 2, 10, 2},
        {0, 3, 5, 1},
        {3, 2, 5, 1}
    };
    std::vector<int> intersections = {0, 1, 2, 3};

    DroneDeliverySystem system(intersections, streets);

    // Delivery request with a tight deadline that only route B can satisfy (total time 10)
    DeliveryRequest request;
    request.start_intersection = 0;
    request.destination_intersection = 2;
    request.deadline = 15;  // only fast route possible
    request.priority = 8;
    request.arrival_time = 0;

    std::vector<int> route = system.plan_route(request);
    // Expected route is 0 -> 3 -> 2
    std::vector<int> expected_route = {0, 3, 2};

    REQUIRE(route == expected_route);
}

TEST_CASE("Plan route handles disconnected destination", "[drone_delivery]") {
    // Graph: intersections {0,1,2} with only one street 0->1.
    std::vector<Street> streets = {
        {0, 1, 10, 2}
    };
    std::vector<int> intersections = {0, 1, 2};

    DroneDeliverySystem system(intersections, streets);

    DeliveryRequest request;
    request.start_intersection = 0;
    request.destination_intersection = 2;  // 2 is disconnected
    request.deadline = 100;
    request.priority = 5;
    request.arrival_time = 0;

    std::vector<int> route = system.plan_route(request);
    // Expect no route since destination is disconnected
    REQUIRE(route.empty());
}