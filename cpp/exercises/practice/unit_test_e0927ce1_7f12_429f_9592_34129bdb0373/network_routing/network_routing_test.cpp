#include "network_routing.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using std::vector;
using std::tuple;

TEST_CASE("Single request shortest path") {
    int N = 4;
    // Graph: 0-1 (5), 1-2 (8), 0-2 (10), 2-3 (2)
    vector<tuple<int, int, int>> connections = {
        {0, 1, 5},
        {1, 2, 8},
        {0, 2, 10},
        {2, 3, 2}
    };
    // Request: from 0 to 3, shortest path is 0-2-3 = 10 + 2 = 12
    vector<tuple<int, int>> requests = {
        {0, 3}
    };
    int result = network_routing::optimize_routing(N, connections, requests);
    REQUIRE(result == 12);
}

TEST_CASE("Multiple requests different paths") {
    int N = 4;
    // Graph: same as above
    vector<tuple<int, int, int>> connections = {
        {0, 1, 5},
        {1, 2, 8},
        {0, 2, 10},
        {2, 3, 2}
    };
    // Requests: (0,1) cost 5 and (2,3) cost 2, maximum among them is 5.
    vector<tuple<int, int>> requests = {
        {0, 1},
        {2, 3}
    };
    int result = network_routing::optimize_routing(N, connections, requests);
    REQUIRE(result == 5);
}

TEST_CASE("Graph with duplicate connections and alternative routes") {
    int N = 5;
    // Graph: Multiple paths with duplicate edge between 1 and 2.
    vector<tuple<int, int, int>> connections = {
        {0, 1, 4},
        {1, 2, 6},
        {0, 2, 10},
        {1, 2, 5},
        {2, 3, 3},
        {3, 4, 15},
        {2, 4, 20}
    };
    // Requests: (0,4) minimal path 0-1-2-3-4 = 4+5+3+15 = 27, 
    // and (1,3) minimal path 1-2-3 = 5+3 = 8.
    // Maximum among them is 27.
    vector<tuple<int, int>> requests = {
        {0, 4},
        {1, 3}
    };
    int result = network_routing::optimize_routing(N, connections, requests);
    REQUIRE(result == 27);
}

TEST_CASE("Graph with cycle and alternative long path") {
    int N = 6;
    // Graph: cycle and alternative direct expensive edge.
    vector<tuple<int, int, int>> connections = {
        {0, 1, 2},
        {1, 2, 2},
        {2, 3, 2},
        {3, 4, 2},
        {4, 5, 2},
        {0, 5, 15},
        {1, 4, 10}
    };
    // Requests:
    // (0,3): best path 0-1-2-3 = 2+2+2 = 6
    // (2,5): best path 2-3-4-5 = 2+2+2 = 6
    // (0,5): best path 0-1-2-3-4-5 = 2+2+2+2+2 = 10
    // Maximum among them is 10.
    vector<tuple<int, int>> requests = {
        {0, 3},
        {2, 5},
        {0, 5}
    };
    int result = network_routing::optimize_routing(N, connections, requests);
    REQUIRE(result == 10);
}

TEST_CASE("Fully connected graph with duplicate edges") {
    int N = 3;
    // Graph: fully connected with duplicate edge between 0 and 1.
    vector<tuple<int, int, int>> connections = {
        {0, 1, 7},
        {0, 1, 3},
        {1, 2, 4},
        {0, 2, 10}
    };
    // Request: (0,2): optimal path is 0-1-2 = 3+4 = 7.
    vector<tuple<int, int>> requests = {
        {0, 2}
    };
    int result = network_routing::optimize_routing(N, connections, requests);
    REQUIRE(result == 7);
}