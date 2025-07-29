#include "network_deploy.h"
#include "catch.hpp"
#include <vector>

using std::vector;

TEST_CASE("Single node without relay stations") {
    int N = 1;
    int R = 0;
    vector<vector<int>> B = { {0} };
    vector<vector<int>> C = { {0} };
    int RelayCost = 5; // arbitrary since there's only one node

    // For a single node, no connection is needed.
    int expected = 0;
    int result = network_deploy::optimal_network_deployment(N, R, B, C, RelayCost);
    REQUIRE(result == expected);
}

TEST_CASE("Provided sample with N=4 and R=2") {
    int N = 4;
    int R = 2;
    vector<vector<int>> B = {
        {0, 5, 2, 1},
        {5, 0, 3, 2},
        {2, 3, 0, 4},
        {1, 2, 4, 0}
    };
    vector<vector<int>> C = {
        {0, 10, 5, 3},
        {10, 0, 7, 4},
        {5, 7, 0, 6},
        {3, 4, 6, 0}
    };
    int RelayCost = 2;

    // Based on the sample explanation, the optimal cost is achieved by connecting all nodes to both relay stations.
    // Total cost = 4 nodes * 2 connections per node * RelayCost = 16.
    int expected = 16;
    int result = network_deploy::optimal_network_deployment(N, R, B, C, RelayCost);
    REQUIRE(result == expected);
}

TEST_CASE("No relay stations forcing direct links (MST scenario)") {
    int N = 3;
    int R = 0;
    // Bandwidth requirements (set arbitrarily, they are assumed to be met if connectivity exists)
    vector<vector<int>> B = {
        {0, 1, 1},
        {1, 0, 1},
        {1, 1, 0}
    };
    // Direct link cost matrix
    vector<vector<int>> C = {
        {0, 3, 4},
        {3, 0, 5},
        {4, 5, 0}
    };
    int RelayCost = 10; // High enough so that relay option is not appealing

    // The optimal way in this case is to use direct links only.
    // The minimum spanning tree (MST) for these nodes has cost: 3 (edge between 0 and 1) + 4 (edge between 0 and 2) = 7.
    int expected = 7;
    int result = network_deploy::optimal_network_deployment(N, R, B, C, RelayCost);
    REQUIRE(result == expected);
}

TEST_CASE("Mixed strategy with one relay station") {
    int N = 5;
    int R = 1;
    // Setting minimal bandwidth requirements for connectivity
    vector<vector<int>> B = {
        {0, 1, 1, 1, 1},
        {1, 0, 1, 1, 1},
        {1, 1, 0, 1, 1},
        {1, 1, 1, 0, 1},
        {1, 1, 1, 1, 0}
    };
    vector<vector<int>> C = {
        {0, 10, 100, 100, 100},
        {10, 0, 5,  100, 100},
        {100, 5,  0, 2,   100},
        {100, 100, 2, 0,   1},
        {100, 100, 100, 1, 0}
    };
    int RelayCost = 3;

    // Strategy analysis:
    // Option 1: Use direct links following MST:
    //   Picking edges: 10 (0-1), 5 (1-2), 2 (2-3), 1 (3-4) = 18.
    // Option 2: Use one relay station which all nodes connect to.
    //   Total relay cost = 5 nodes * 3 = 15.
    // Optimal cost = 15.
    int expected = 15;
    int result = network_deploy::optimal_network_deployment(N, R, B, C, RelayCost);
    REQUIRE(result == expected);
}

TEST_CASE("Abundant relay stations favor relay-only strategy") {
    int N = 3;
    int R = 3;
    vector<vector<int>> B = {
        {0, 1, 1},
        {1, 0, 1},
        {1, 1, 0}
    };
    // Set direct link costs high to force use of relay stations.
    vector<vector<int>> C = {
        {0, 50, 50},
        {50, 0, 50},
        {50, 50, 0}
    };
    int RelayCost = 1;

    // Optimal solution: connect each node to a relay station.
    // Total cost = 3 nodes * 1 = 3.
    int expected = 3;
    int result = network_deploy::optimal_network_deployment(N, R, B, C, RelayCost);
    REQUIRE(result == expected);
}