#include <vector>
#include <tuple>
#include <cmath>
#include "catch.hpp"
#include "quantum_routing.h"

using std::vector;
using std::tuple;

TEST_CASE("Basic Routing Test") {
    vector<tuple<int, int, double>> edges = { {0, 1, 10}, {0, 2, 15}, {1, 2, 5}, {1, 3, 20}, {2, 3, 10} };
    vector<tuple<int, int, double>> requests = { {0, 3, 0.8}, {1, 2, 0.9} };
    vector<double> results = quantum_routing::optimal_routes(4, edges, requests, 50);
    REQUIRE(results.size() == 2);
    REQUIRE(std::abs(results[0] - 25.000000) < 1e-6);
    REQUIRE(std::abs(results[1] - 5.000000) < 1e-6);
}

TEST_CASE("Disconnected Graph returns -1") {
    vector<tuple<int, int, double>> edges = { {0, 1, 10} };
    vector<tuple<int, int, double>> requests = { {0, 2, 0.5} };
    vector<double> results = quantum_routing::optimal_routes(3, edges, requests, 100);
    REQUIRE(results.size() == 1);
    REQUIRE(results[0] == -1);
}

TEST_CASE("Same Source Destination returns 0") {
    vector<tuple<int, int, double>> edges = { {0, 1, 10}, {1, 2, 20} };
    vector<tuple<int, int, double>> requests = { {1, 1, 0.9} };
    vector<double> results = quantum_routing::optimal_routes(3, edges, requests, 100);
    REQUIRE(results.size() == 1);
    REQUIRE(std::abs(results[0] - 0.0) < 1e-6);
}

TEST_CASE("Route Exceeds K returns -1") {
    vector<tuple<int, int, double>> edges = { {0, 1, 40}, {1, 2, 40} };
    vector<tuple<int, int, double>> requests = { {0, 2, 0.7} };
    vector<double> results = quantum_routing::optimal_routes(3, edges, requests, 50);
    REQUIRE(results.size() == 1);
    REQUIRE(results[0] == -1);
}

TEST_CASE("Multiple Edges, Optimal Choice Test") {
    vector<tuple<int, int, double>> edges = { {0, 1, 10}, {0, 1, 20}, {1, 2, 15} };
    vector<tuple<int, int, double>> requests = { {0, 2, 0.95} };
    vector<double> results = quantum_routing::optimal_routes(3, edges, requests, 30);
    REQUIRE(results.size() == 1);
    REQUIRE(std::abs(results[0] - 25.000000) < 1e-6);
}

TEST_CASE("Cycle graph, multiple valid routes") {
    vector<tuple<int, int, double>> edges = { {0, 1, 5}, {1, 2, 10}, {2, 3, 5}, {3, 0, 10}, {0, 2, 20} };
    vector<tuple<int, int, double>> requests = { {0, 2, 0.99} };
    vector<double> results = quantum_routing::optimal_routes(4, edges, requests, 50);
    REQUIRE(results.size() == 1);
    REQUIRE(std::abs(results[0] - 15.000000) < 1e-6);
}