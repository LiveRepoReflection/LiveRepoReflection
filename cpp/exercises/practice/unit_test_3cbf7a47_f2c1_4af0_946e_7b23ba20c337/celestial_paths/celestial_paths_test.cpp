#include "celestial_paths.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include "catch.hpp"

namespace {
    bool are_equal(double a, double b, double epsilon = 1e-6) {
        return std::fabs(a - b) < epsilon;
    }
}

TEST_CASE("Basic path test", "[basic]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 2},
        {0, 2, 2, 3},
        {1, 2, 3, 4},
        {2, 3, 4, 5}
    };
    
    celestial_paths::CelestialNetwork network(4, wormholes);
    
    double prob = network.calculate_probability(0, 3, 10);
    
    REQUIRE(prob >= 0.0);
    REQUIRE(prob <= 1.0);
}

TEST_CASE("No path exists", "[no_path]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 2},
        {2, 3, 4, 5}
    };
    
    celestial_paths::CelestialNetwork network(4, wormholes);
    
    double prob = network.calculate_probability(0, 3, 10);
    
    REQUIRE(are_equal(prob, 0.0));
}

TEST_CASE("Exact time limit", "[exact_time]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 5, 5}
    };
    
    celestial_paths::CelestialNetwork network(2, wormholes);
    
    double prob = network.calculate_probability(0, 1, 5);
    
    REQUIRE(are_equal(prob, 1.0));
}

TEST_CASE("Single path with varying times", "[single_path]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 3, 7}
    };
    
    celestial_paths::CelestialNetwork network(2, wormholes);
    
    SECTION("Time limit within minimum range") {
        double prob = network.calculate_probability(0, 1, 2);
        REQUIRE(are_equal(prob, 0.0));
    }
    
    SECTION("Time limit at minimum range") {
        double prob = network.calculate_probability(0, 1, 3);
        REQUIRE(are_equal(prob, 0.0, 0.01)); // close to 0 due to boundary
    }
    
    SECTION("Time limit in middle of range") {
        double prob = network.calculate_probability(0, 1, 5);
        REQUIRE(are_equal(prob, 0.5, 0.01));
    }
    
    SECTION("Time limit at maximum range") {
        double prob = network.calculate_probability(0, 1, 7);
        REQUIRE(are_equal(prob, 1.0, 0.01)); // close to 1 due to boundary
    }
    
    SECTION("Time limit beyond maximum range") {
        double prob = network.calculate_probability(0, 1, 10);
        REQUIRE(are_equal(prob, 1.0));
    }
}

TEST_CASE("Multiple paths between stations", "[multiple_paths]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 5},
        {1, 2, 1, 5},
        {0, 2, 5, 10}
    };
    
    celestial_paths::CelestialNetwork network(3, wormholes);
    
    double prob = network.calculate_probability(0, 2, 6);
    
    REQUIRE(prob > 0.0);
    REQUIRE(prob < 1.0);
}

TEST_CASE("Self to self travel", "[self_travel]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 2},
        {1, 2, 3, 4}
    };
    
    celestial_paths::CelestialNetwork network(3, wormholes);
    
    double prob = network.calculate_probability(0, 0, 5);
    
    REQUIRE(are_equal(prob, 1.0));
}

TEST_CASE("Complex network test", "[complex]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 3},
        {1, 2, 2, 4},
        {2, 3, 1, 2},
        {3, 4, 3, 5},
        {0, 4, 10, 15},
        {0, 2, 5, 8}
    };
    
    celestial_paths::CelestialNetwork network(5, wormholes);
    
    SECTION("Short time limit") {
        double prob = network.calculate_probability(0, 4, 7);
        REQUIRE(prob >= 0.0);
        REQUIRE(prob <= 1.0);
    }
    
    SECTION("Medium time limit") {
        double prob = network.calculate_probability(0, 4, 10);
        REQUIRE(prob >= 0.0);
        REQUIRE(prob <= 1.0);
    }
    
    SECTION("Long time limit") {
        double prob = network.calculate_probability(0, 4, 20);
        REQUIRE(are_equal(prob, 1.0));
    }
}

TEST_CASE("Large network test", "[large]") {
    std::vector<std::tuple<int, int, int, int>> wormholes;
    const int n = 20;  // 20 nodes
    
    // Create a dense network
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            wormholes.push_back({i, j, 1 + (i * j) % 5, 5 + (i * j) % 10});
        }
    }
    
    celestial_paths::CelestialNetwork network(n, wormholes);
    
    double prob = network.calculate_probability(0, n-1, 15);
    
    REQUIRE(prob >= 0.0);
    REQUIRE(prob <= 1.0);
}

TEST_CASE("Integration test from example", "[example]") {
    std::vector<std::tuple<int, int, int, int>> wormholes = {
        {0, 1, 1, 2},
        {0, 2, 2, 3},
        {1, 2, 3, 4},
        {2, 3, 4, 5}
    };
    
    celestial_paths::CelestialNetwork network(4, wormholes);
    
    double prob = network.calculate_probability(0, 3, 10);
    
    // For this test, we're just checking that the implementation runs without errors
    // The exact probability value depends on the implementation approach and would
    // need to be validated against an expected value
    REQUIRE(prob >= 0.0);
    REQUIRE(prob <= 1.0);
}

TEST_CASE("Edge case with maximum constraints", "[constraints]") {
    const int n = 50;  // Maximum number of nodes
    std::vector<std::tuple<int, int, int, int>> wormholes;
    
    // Create some connections to ensure graph is connected
    for (int i = 0; i < n-1; ++i) {
        wormholes.push_back({i, i+1, 50, 100});  // Use maximum traversal times
    }
    
    celestial_paths::CelestialNetwork network(n, wormholes);
    
    double prob = network.calculate_probability(0, n-1, 5000);
    
    // For a time limit of 5000, which is more than the maximum possible traversal time,
    // the probability should be 1.0
    REQUIRE(are_equal(prob, 1.0));
}