#include "traffic_tolls.h"
#include "catch.hpp"
#include <vector>
#include <cmath>

using namespace std;

// Test case: Basic single edge route where a valid toll is computed.
TEST_CASE("Basic single edge route", "[traffic_tolls]") {
    vector<Edge> edges = { {0, 1, 10, 500, 400} };
    double tollSensitivity = 0.1;
    double budget = 100.0;
    int source = 0, destination = 1;
    vector<double> result = optimizeTolls(edges, tollSensitivity, budget, source, destination);
    
    // Expect the result size to match the number of edges.
    REQUIRE(result.size() == edges.size());
    
    // All computed tolls should be non-negative and not an error signal.
    for (auto toll : result) {
        REQUIRE(toll >= 0.0);
        REQUIRE(toll != -1);
    }
}

// Test case: Multiple Paths with valid optimization.
TEST_CASE("Multiple paths optimization", "[traffic_tolls]") {
    vector<Edge> edges = {
         {0, 1, 10, 500, 400},
         {0, 2, 15, 600, 500},
         {1, 2, 8, 400, 300},
         {1, 3, 12, 700, 600},
         {2, 3, 10, 500, 400}
    };
    double tollSensitivity = 0.1;
    double budget = 500.0;
    int source = 0, destination = 3;
    vector<double> result = optimizeTolls(edges, tollSensitivity, budget, source, destination);
    
    // Expect the result size to match the number of edges.
    REQUIRE(result.size() == edges.size());
    
    // Verify that tolls are non-negative.
    bool anyTollSet = false;
    for (auto toll : result) {
        REQUIRE(toll >= 0.0);
        if(toll > 1e-6) {
            anyTollSet = true;
        }
    }
    // With sufficient budget, at least one toll adjustment is expected.
    REQUIRE(anyTollSet);
}

// Test case: Graph with no path from source to destination should yield error signals.
// In this scenario, the function is expected to return a vector of length equal to the
// number of edges with each element set to -1.
TEST_CASE("No path exists", "[traffic_tolls]") {
    vector<Edge> edges = {
         {0, 1, 10, 500, 400},
         {2, 3, 12, 700, 600}
    };
    double tollSensitivity = 0.1;
    double budget = 300.0;
    int source = 0, destination = 3;
    vector<double> result = optimizeTolls(edges, tollSensitivity, budget, source, destination);
    
    REQUIRE(result.size() == edges.size());
    for (auto toll : result) {
        REQUIRE(toll == -1);
    }
}

// Test case: Budget insufficient to have a meaningful effect.
// Here, when the budget is too low, the function should return a singleton vector { -1 }.
TEST_CASE("Insufficient budget", "[traffic_tolls]") {
    vector<Edge> edges = {
         {0, 1, 10, 500, 400},
         {1, 2, 8, 400, 300},
         {2, 3, 10, 500, 400}
    };
    double tollSensitivity = 0.1;
    double budget = 0.0;
    int source = 0, destination = 3;
    vector<double> result = optimizeTolls(edges, tollSensitivity, budget, source, destination);
    
    // Expect a singleton error result.
    REQUIRE(result.size() == 1);
    REQUIRE(result[0] == -1);
}

// Test case: Complex network scenario across multiple edges.
// Verifies that the computed tolls yield total toll revenue within the available budget.
TEST_CASE("Complex network test", "[traffic_tolls]") {
    vector<Edge> edges = {
         {0, 1, 12, 800, 600},
         {0, 2, 10, 700, 500},
         {1, 2, 9, 600, 400},
         {1, 3, 15, 900, 800},
         {2, 3, 11, 650, 550},
         {2, 4, 14, 800, 750},
         {3, 4, 10, 700, 650},
         {4, 5, 8, 500, 450}
    };
    double tollSensitivity = 0.2;
    double budget = 1000.0;
    int source = 0, destination = 5;
    vector<double> result = optimizeTolls(edges, tollSensitivity, budget, source, destination);
    
    // Expect the result size to match the number of edges.
    REQUIRE(result.size() == edges.size());
    
    // All tolls should be non-negative.
    for (auto toll : result) {
         REQUIRE(toll >= 0.0);
    }
    
    // Compute the total toll revenue using the demand function.
    double totalRevenue = 0.0;
    for (size_t i = 0; i < edges.size(); ++i) {
         double vehicles_after = edges[i].initial_vehicles * exp(-tollSensitivity * result[i]);
         totalRevenue += result[i] * vehicles_after;
    }
    // The computed total toll revenue should not exceed the budget.
    REQUIRE(totalRevenue <= budget + 1e-6);
}