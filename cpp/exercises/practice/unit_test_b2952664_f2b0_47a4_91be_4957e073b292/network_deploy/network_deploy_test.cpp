#include "network_deploy.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using std::vector;
using std::tuple;
using std::make_tuple;

TEST_CASE("no_coverage_possible", "[network_deploy]") {
    int N = 5, M = 5;
    vector<tuple<int, int, int, int>> baseStations = {
        make_tuple(1, 1, 10, 1),
        make_tuple(3, 3, 10, 1)
    };
    int T = 100; // Threshold too high for any station to provide sufficient coverage.
    vector<int> result = network_deploy::optimal_network_deploy(N, M, baseStations, T);
    // Expecting an empty deployment, because coverage conditions are unmet.
    CHECK(result.empty());
}

TEST_CASE("single_station_coverage", "[network_deploy]") {
    int N = 3, M = 3;
    vector<tuple<int, int, int, int>> baseStations = {
        make_tuple(1, 1, 50, 1)
    };
    int T = 30;
    vector<int> result = network_deploy::optimal_network_deploy(N, M, baseStations, T);
    // Only one candidate exists, deployment should include it if it provides coverage.
    REQUIRE(result.size() == 1);
    CHECK(result[0] == 0);
}

TEST_CASE("duplicate_station_positions", "[network_deploy]") {
    int N = 10, M = 10;
    vector<tuple<int, int, int, int>> baseStations = {
        make_tuple(2, 2, 40, 2),
        make_tuple(2, 2, 40, 2),
        make_tuple(5, 5, 60, 1),
        make_tuple(8, 8, 70, 3)
    };
    int T = 35;
    vector<int> result = network_deploy::optimal_network_deploy(N, M, baseStations, T);
    // The algorithm should handle duplicate positions and return valid indices.
    for (int idx : result) {
        CHECK(idx >= 0);
        CHECK(idx < static_cast<int>(baseStations.size()));
    }
}

TEST_CASE("all_stations_deployment_balance", "[network_deploy]") {
    int N = 15, M = 15;
    vector<tuple<int, int, int, int>> baseStations = {
        make_tuple(1, 1, 30, 2),
        make_tuple(1, 13, 30, 2),
        make_tuple(13, 1, 30, 2),
        make_tuple(13, 13, 30, 2),
        make_tuple(7, 7, 50, 3)
    };
    int T = 25;
    vector<int> result = network_deploy::optimal_network_deploy(N, M, baseStations, T);
    // Deployment should balance coverage and interference.
    for (int idx : result) {
        CHECK(idx >= 0);
        CHECK(idx < static_cast<int>(baseStations.size()));
    }
}

TEST_CASE("complex_scenario", "[network_deploy]") {
    int N = 20, M = 20;
    vector<tuple<int, int, int, int>> baseStations = {
        make_tuple(2, 3, 80, 2),
        make_tuple(4, 5, 45, 1),
        make_tuple(6, 7, 70, 2),
        make_tuple(8, 9, 60, 1),
        make_tuple(10, 11, 55, 3),
        make_tuple(12, 13, 90, 2),
        make_tuple(14, 15, 65, 1),
        make_tuple(16, 17, 75, 2),
        make_tuple(18, 19, 85, 3),
        make_tuple(0, 0, 50, 2)
    };
    int T = 50;
    vector<int> result = network_deploy::optimal_network_deploy(N, M, baseStations, T);
    // Check that returned indices are valid and there are no duplicates.
    vector<bool> seen(baseStations.size(), false);
    for (int idx : result) {
        CHECK(idx >= 0);
        CHECK(idx < static_cast<int>(baseStations.size()));
        CHECK(!seen[idx]);
        seen[idx] = true;
    }
}