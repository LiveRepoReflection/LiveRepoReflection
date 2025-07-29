#include "network_routing.h"
#include <vector>
#include "catch.hpp"

TEST_CASE("empty_network", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(3);
    REQUIRE(routing.find_best_path(0, 2, 100, 1000).empty());
}

TEST_CASE("direct_connection", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(3);
    routing.add_connection(0, 2, 50, 500);
    std::vector<int> expected = {0, 2};
    REQUIRE(routing.find_best_path(0, 2, 400, 100) == expected);
}

TEST_CASE("bandwidth_constraint", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(3);
    routing.add_connection(0, 1, 20, 300);
    routing.add_connection(1, 2, 30, 200);
    REQUIRE(routing.find_best_path(0, 2, 250, 100).empty());
}

TEST_CASE("latency_constraint", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(3);
    routing.add_connection(0, 1, 60, 500);
    routing.add_connection(1, 2, 60, 500);
    REQUIRE(routing.find_best_path(0, 2, 400, 100).empty());
}

TEST_CASE("multiple_paths", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(5);
    routing.add_connection(0, 1, 20, 500);
    routing.add_connection(1, 2, 30, 600);
    routing.add_connection(0, 3, 50, 400);
    routing.add_connection(3, 4, 10, 700);
    routing.add_connection(2, 4, 40, 300);
    routing.add_connection(0, 4, 50, 500);
    
    std::vector<int> expected = {0, 4};
    REQUIRE(routing.find_best_path(0, 4, 450, 100) == expected);
}

TEST_CASE("tie_breaker_latency", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(4);
    routing.add_connection(0, 1, 20, 500);
    routing.add_connection(1, 3, 30, 500);
    routing.add_connection(0, 2, 25, 500);
    routing.add_connection(2, 3, 20, 500);
    
    std::vector<int> expected = {0, 2, 3};
    REQUIRE(routing.find_best_path(0, 3, 400, 100) == expected);
}

TEST_CASE("tie_breaker_lexicographical", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(4);
    routing.add_connection(0, 1, 20, 500);
    routing.add_connection(1, 3, 20, 500);
    routing.add_connection(0, 2, 20, 500);
    routing.add_connection(2, 3, 20, 500);
    
    std::vector<int> expected = {0, 1, 3};
    REQUIRE(routing.find_best_path(0, 3, 400, 100) == expected);
}

TEST_CASE("dynamic_network", "[find_best_path]") {
    NetworkRouting routing;
    routing.initialize(3);
    routing.add_connection(0, 1, 20, 500);
    routing.add_connection(1, 2, 30, 600);
    
    std::vector<int> expected = {0, 1, 2};
    REQUIRE(routing.find_best_path(0, 2, 400, 100) == expected);
    
    routing.remove_connection(1, 2);
    REQUIRE(routing.find_best_path(0, 2, 400, 100).empty());
    
    routing.add_connection(0, 2, 50, 500);
    expected = {0, 2};
    REQUIRE(routing.find_best_path(0, 2, 400, 100) == expected);
}