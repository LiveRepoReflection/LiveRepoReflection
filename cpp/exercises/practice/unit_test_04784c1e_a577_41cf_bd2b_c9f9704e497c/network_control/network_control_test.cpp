#include "catch.hpp"
#include "network_control.h"
#include <unordered_map>
#include <vector>
#include <cmath>

const double EPSILON = 1e-6;

bool approx_equal(double a, double b) {
    return std::abs(a - b) < EPSILON;
}

TEST_CASE("Single node with no outgoing links") {
    NetworkNode node(0, 1, {});
    
    std::unordered_map<int, double> congestion_factors;
    node.update_rates(congestion_factors);
    
    REQUIRE(approx_equal(node.get_rate(0), 0.0));
}

TEST_CASE("Node with single outgoing link") {
    NetworkNode node(0, 2, {{1, 100}});
    
    SECTION("Initial rate should be 1.0") {
        REQUIRE(approx_equal(node.get_rate(1), 1.0));
    }
    
    SECTION("No congestion should increase rate") {
        std::unordered_map<int, double> congestion_factors{{1, 0.5}};
        node.update_rates(congestion_factors);
        REQUIRE(approx_equal(node.get_rate(1), 1.1));
    }
    
    SECTION("High congestion should decrease rate") {
        std::unordered_map<int, double> congestion_factors{{1, 0.95}};
        node.update_rates(congestion_factors);
        REQUIRE(approx_equal(node.get_rate(1), 0.5));
    }
}

TEST_CASE("Node with multiple outgoing links") {
    NetworkNode node(0, 3, {{1, 100}, {2, 200}});
    
    SECTION("Initial rates should be 1.0") {
        REQUIRE(approx_equal(node.get_rate(1), 1.0));
        REQUIRE(approx_equal(node.get_rate(2), 1.0));
    }
    
    SECTION("Mixed congestion updates") {
        std::unordered_map<int, double> congestion_factors{{1, 0.5}, {2, 0.95}};
        node.update_rates(congestion_factors);
        REQUIRE(approx_equal(node.get_rate(1), 1.1));
        REQUIRE(approx_equal(node.get_rate(2), 0.5));
    }
}

TEST_CASE("Edge cases and constraints") {
    NetworkNode node(0, 4, {{1, 100}, {2, 200}, {3, 300}});
    
    SECTION("Non-existent link") {
        REQUIRE(approx_equal(node.get_rate(10), 0.0));
    }
    
    SECTION("Maximum rate constraint") {
        // Simulate multiple increases to reach max_rate
        std::unordered_map<int, double> low_congestion{{1, 0.1}};
        for(int i = 0; i < 10000; i++) {
            node.update_rates(low_congestion);
        }
        REQUIRE(approx_equal(node.get_rate(1), 1000.0)); // max_rate
    }
    
    SECTION("Minimum rate constraint") {
        std::unordered_map<int, double> high_congestion{{1, 2.0}};
        for(int i = 0; i < 100; i++) {
            node.update_rates(high_congestion);
        }
        REQUIRE(approx_equal(node.get_rate(1), 0.0));
    }
}

TEST_CASE("Stability test") {
    NetworkNode node(0, 2, {{1, 100}});
    
    SECTION("Rate should stabilize with moderate congestion") {
        std::unordered_map<int, double> moderate_congestion{{1, 0.8}};
        double initial_rate = node.get_rate(1);
        
        // Multiple updates with same congestion
        for(int i = 0; i < 10; i++) {
            node.update_rates(moderate_congestion);
        }
        
        REQUIRE(approx_equal(node.get_rate(1), initial_rate));
    }
}

TEST_CASE("Large network test") {
    std::vector<std::pair<int, int>> many_links;
    for(int i = 1; i < 1000; i++) {
        many_links.push_back({i, 100});
    }
    
    NetworkNode node(0, 1000, many_links);
    
    std::unordered_map<int, double> congestion_factors;
    for(int i = 1; i < 1000; i++) {
        congestion_factors[i] = 0.5;
    }
    
    // Should handle large number of links efficiently
    node.update_rates(congestion_factors);
    
    REQUIRE(approx_equal(node.get_rate(500), 1.1));
}

TEST_CASE("Complex congestion patterns") {
    NetworkNode node(0, 4, {{1, 100}, {2, 200}, {3, 300}});
    
    SECTION("Oscillating congestion") {
        std::unordered_map<int, double> high_congestion{{1, 0.95}};
        std::unordered_map<int, double> low_congestion{{1, 0.5}};
        
        double initial_rate = node.get_rate(1);
        
        for(int i = 0; i < 10; i++) {
            node.update_rates(high_congestion);
            node.update_rates(low_congestion);
        }
        
        // Rate should not be wildly different from initial rate
        REQUIRE(node.get_rate(1) >= initial_rate * 0.1);
        REQUIRE(node.get_rate(1) <= initial_rate * 10.0);
    }
}