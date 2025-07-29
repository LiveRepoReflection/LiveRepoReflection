#include "traffic_flow.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using Edge = std::tuple<int, int, int>;

TEST_CASE("Direct path available") {
    // Graph: 0 -> 1 with capacity 10
    // k = 2, cars = 5, trucks = 3.
    // Constraint: x + 2y <= 10, with x<=5, y<=3. Maximum vehicles: 7 (e.g., 5 cars and 2 trucks or 4 cars and 3 trucks).
    int n = 2;
    int source = 0;
    int destination = 1;
    int k = 2;
    int numCars = 5;
    int numTrucks = 3;
    std::vector<Edge> edges = { std::make_tuple(0, 1, 10) };

    int expected = 7;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}

TEST_CASE("Disconnected graph") {
    // Graph: No edge from source to destination.
    int n = 3;
    int source = 0;
    int destination = 2;
    int k = 3;
    int numCars = 10;
    int numTrucks = 10;
    std::vector<Edge> edges = {
        std::make_tuple(0, 1, 5),
        std::make_tuple(1, 0, 5)
    };

    int expected = 0;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}

TEST_CASE("Multiple paths with parallel routes") {
    // Graph:
    // 0 -> 1 (capacity 6)
    // 0 -> 2 (capacity 6)
    // 1 -> 3 (capacity 6)
    // 2 -> 3 (capacity 6)
    // k = 3, numCars = 4, numTrucks = 4.
    // Two independent paths allow split flow.
    int n = 4;
    int source = 0;
    int destination = 3;
    int k = 3;
    int numCars = 4;
    int numTrucks = 4;
    std::vector<Edge> edges = {
        std::make_tuple(0, 1, 6),
        std::make_tuple(0, 2, 6),
        std::make_tuple(1, 3, 6),
        std::make_tuple(2, 3, 6)
    };

    // Optimal distribution can send 6 vehicles in total.
    int expected = 6;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}

TEST_CASE("Graph with cycle and multiple routes") {
    // Graph:
    // 0 -> 1 (capacity 100)
    // 1 -> 2 (capacity 5)
    // 0 -> 2 (capacity 3)
    // 2 -> 3 (capacity 5)
    // 1 -> 3 (capacity 7)
    // k = 4, numCars = 10, numTrucks = 10.
    // Even with cycles, capacity limits along bottlenecks restrict the maximum vehicles.
    int n = 4;
    int source = 0;
    int destination = 3;
    int k = 4;
    int numCars = 10;
    int numTrucks = 10;
    std::vector<Edge> edges = {
        std::make_tuple(0, 1, 100),
        std::make_tuple(1, 2, 5),
        std::make_tuple(0, 2, 3),
        std::make_tuple(2, 3, 5),
        std::make_tuple(1, 3, 7)
    };

    // Based on the capacities and cost (truck uses 4) it is optimal to use primarily cars.
    // The expected maximum vehicles computed based on optimal flow distribution is 10.
    int expected = 10;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}

TEST_CASE("Truck only scenario") {
    // Graph: 0 -> 1 with capacity 10.
    // k = 2, numCars = 0, numTrucks = 10.
    // Each truck uses 2 units; maximum trucks = floor(10 / 2) = 5.
    int n = 2;
    int source = 0;
    int destination = 1;
    int k = 2;
    int numCars = 0;
    int numTrucks = 10;
    std::vector<Edge> edges = { std::make_tuple(0, 1, 10) };

    int expected = 5;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}

TEST_CASE("No vehicles available") {
    // Graph: 0 -> 1 with capacity 50.
    // k = 3, numCars = 0, numTrucks = 0.
    // With no vehicles, expected maximum vehicles is 0.
    int n = 2;
    int source = 0;
    int destination = 1;
    int k = 3;
    int numCars = 0;
    int numTrucks = 0;
    std::vector<Edge> edges = { std::make_tuple(0, 1, 50) };

    int expected = 0;
    int result = traffic_flow::maxVehicles(n, source, destination, k, numCars, numTrucks, edges);
    REQUIRE(result == expected);
}