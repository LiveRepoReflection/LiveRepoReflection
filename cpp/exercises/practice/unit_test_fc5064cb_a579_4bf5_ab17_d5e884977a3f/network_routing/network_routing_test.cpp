#include "network_routing.h"
#include "catch.hpp"
#include <vector>
#include <string>

TEST_CASE("Basic routing with sufficient capacity") {
    NetworkRouting nr(5, {1, 1, 1, 1, 1});
    nr.addEdge(0, 1, 10, 0);
    nr.addEdge(1, 2, 5, 1);
    nr.addEdge(2, 3, 5, 2);
    nr.addEdge(3, 4, 10, 3);
    
    auto path = nr.route(0, 4, 4);
    REQUIRE(path == std::vector<int>{0, 1, 2, 3, 4});
}

TEST_CASE("Routing after edge removal") {
    NetworkRouting nr(5, {1, 1, 1, 1, 1});
    nr.addEdge(0, 1, 10, 0);
    nr.addEdge(1, 2, 5, 1);
    nr.addEdge(2, 3, 5, 2);
    nr.addEdge(3, 4, 10, 3);
    nr.removeEdge(2, 3, 5);
    
    auto path = nr.route(0, 4, 6);
    REQUIRE(path == std::vector<int>{});
}

TEST_CASE("Node capacity constraints") {
    NetworkRouting nr(3, {0, 1, 1}); // Node 0 has 0 capacity
    nr.addEdge(0, 1, 5, 0);
    nr.addEdge(1, 2, 5, 1);
    
    auto path = nr.route(0, 2, 2);
    REQUIRE(path == std::vector<int>{});
}

TEST_CASE("Multiple routes with capacity consumption") {
    NetworkRouting nr(3, {1, 1, 1});
    nr.addEdge(0, 1, 5, 0);
    nr.addEdge(1, 2, 5, 0);
    
    auto path1 = nr.route(0, 2, 1);
    REQUIRE(path1 == std::vector<int>{0, 1, 2});
    
    auto path2 = nr.route(0, 2, 2);
    REQUIRE(path2 == std::vector<int>{});
}

TEST_CASE("Edge weight update") {
    NetworkRouting nr(3, {1, 1, 1});
    nr.addEdge(0, 1, 5, 0);
    nr.addEdge(1, 2, 5, 0);
    nr.addEdge(0, 1, 1, 1); // Update weight
    
    auto path = nr.route(0, 2, 2);
    REQUIRE(path == std::vector<int>{0, 1, 2});
}

TEST_CASE("Disconnected graph") {
    NetworkRouting nr(4, {1, 1, 1, 1});
    nr.addEdge(0, 1, 5, 0);
    nr.addEdge(2, 3, 5, 0);
    
    auto path = nr.route(0, 3, 1);
    REQUIRE(path == std::vector<int>{});
}

TEST_CASE("Large timestamp ordering") {
    NetworkRouting nr(3, {1, 1, 1});
    nr.addEdge(0, 1, 5, 1000000000);
    nr.addEdge(1, 2, 5, 1000000000);
    
    auto path = nr.route(0, 2, 1000000001);
    REQUIRE(path == std::vector<int>{0, 1, 2});
}