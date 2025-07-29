#include "network_routing.h"
#include "catch.hpp"
#include <unordered_map>
#include <vector>
#include <tuple>
#include <string>
#include <limits>

using Graph = std::unordered_map<std::string, std::vector<std::pair<std::string, int>>>;
using Transfer = std::tuple<std::string, std::string, int>;

TEST_CASE("Single direct transfer") {
    // Graph: A -5- B
    Graph graph;
    graph["A"] = { {"B", 5} };
    graph["B"] = { {"A", 5} };
    
    std::vector<Transfer> transfers = {
        {"A", "B", 10}
    };
    
    // For direct transfer: congestion = 10, cost = 5 * 10 = 50, expected sum = 60
    double expected = 60;
    double result = network_routing::optimize_network_routing(graph, transfers);
    CHECK(result == Approx(expected));
}

TEST_CASE("Two path comparison") {
    // Graph:
    // A -> B: cost 4, B -> C: cost 8, and A -> C (direct): cost 15
    Graph graph;
    graph["A"] = { {"B", 4}, {"C", 15} };
    graph["B"] = { {"A", 4}, {"C", 8} };
    graph["C"] = { {"A", 15}, {"B", 8} };
    
    std::vector<Transfer> transfers = {
        {"A", "C", 5}
    };
    
    // Option 1: A-B-C: congestion = 5 on both edges, cost = 4*5 + 8*5 = 20 + 40 = 60, total = 65
    // Option 2: A-C direct: congestion = 5, cost = 15*5 = 75, total = 80
    // Expected optimal = 65
    double expected = 65;
    double result = network_routing::optimize_network_routing(graph, transfers);
    CHECK(result == Approx(expected));
}

TEST_CASE("Multiple transfers with complex routing") {
    // Graph:
    // A -B: cost 2, A -C: cost 3, B -D: cost 4, C -D: cost 1, B -C: cost 2
    Graph graph;
    graph["A"] = { {"B", 2}, {"C", 3} };
    graph["B"] = { {"A", 2}, {"D", 4}, {"C", 2} };
    graph["C"] = { {"A", 3}, {"D", 1}, {"B", 2} };
    graph["D"] = { {"B", 4}, {"C", 1} };
    
    std::vector<Transfer> transfers = {
        {"A", "D", 3},
        {"B", "C", 4}
    };
    
    // Expected routing:
    // For A->D: optimal via A-C-D: congestion 3, cost = 3*3 + 1*3 = 9 + 3 = 12.
    // For B->C: direct route B-C: congestion 4, cost = 2*4 = 8.
    // Maximum cable congestion = max(3,4) = 4; total cost = 12 + 8 = 20; sum = 4 + 20 = 24.
    double expected = 24;
    double result = network_routing::optimize_network_routing(graph, transfers);
    CHECK(result == Approx(expected));
}

TEST_CASE("No available route") {
    // Graph: A -- B exists, but no connection for C.
    Graph graph;
    graph["A"] = { {"B", 5} };
    graph["B"] = { {"A", 5} };
    graph["C"] = {}; // isolated node
    
    std::vector<Transfer> transfers = {
        {"A", "C", 7}
    };
    
    // Expected: since there's no path from A to C, function should return infinity.
    double expected = std::numeric_limits<double>::infinity();
    double result = network_routing::optimize_network_routing(graph, transfers);
    CHECK(result == expected);
}

TEST_CASE("Cycle in graph with multiple equal paths") {
    // Graph forming a cycle: A - B - C - A, all edges cost 1.
    Graph graph;
    graph["A"] = { {"B", 1}, {"C", 1} };
    graph["B"] = { {"A", 1}, {"C", 1} };
    graph["C"] = { {"A", 1}, {"B", 1} };
    
    std::vector<Transfer> transfers = {
        {"A", "B", 4}
    };
    
    // Optimal is direct A-B: cost = 1*4 = 4, congestion = 4, total = 8.
    double expected = 8;
    double result = network_routing::optimize_network_routing(graph, transfers);
    CHECK(result == Approx(expected));
}