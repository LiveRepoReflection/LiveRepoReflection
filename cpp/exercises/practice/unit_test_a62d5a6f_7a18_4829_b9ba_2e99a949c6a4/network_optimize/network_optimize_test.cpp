#include "network_optimize.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

TEST_CASE("Basic network test") {
    int N = 4;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 5},
        {2, 3, 15},
        {0, 3, 8}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 2, 4},
        {1, 3, 3},
        {0, 3, 7}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Single node network") {
    int N = 1;
    std::vector<std::tuple<int, int, int>> edges = {};
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 0, 5}  // Self-loop query
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Zero bandwidth queries") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 1},
        {1, 2, 1}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 2, 0},
        {1, 2, 0},
        {0, 1, 0}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Insufficient bandwidth") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 5},
        {1, 2, 3}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 2, 4}  // Cannot route 4 units through a 3-unit bottleneck
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == false);
}

TEST_CASE("Multiple paths available") {
    int N = 4;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 10},
        {2, 3, 10},
        {0, 2, 5},
        {1, 3, 5}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 3, 15}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Multiple edges between same nodes") {
    int N = 3;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 5},
        {0, 1, 5},  // Duplicate edge
        {1, 2, 8}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 2, 8}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Complex network with multiple simultaneous queries") {
    int N = 6;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 8},
        {2, 3, 12},
        {3, 4, 7},
        {4, 5, 9},
        {0, 2, 5},
        {1, 3, 6},
        {2, 4, 4},
        {3, 5, 8}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 5, 3},
        {1, 4, 2},
        {2, 5, 4},
        {0, 3, 2}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Maximum size network") {
    int N = 1000;
    std::vector<std::tuple<int, int, int>> edges;
    // Create a simple chain of nodes with sufficient bandwidth
    for(int i = 0; i < N-1; i++) {
        edges.push_back({i, i+1, 1000});
    }
    std::vector<std::tuple<int, int, int>> queries = {
        {0, N-1, 500}
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}

TEST_CASE("Edge cases") {
    int N = 5;
    std::vector<std::tuple<int, int, int>> edges = {
        {0, 1, 0},  // Zero bandwidth edge
        {1, 2, 1},
        {2, 3, 1},
        {3, 4, 1}
    };
    std::vector<std::tuple<int, int, int>> queries = {
        {0, 4, 0},  // Zero bandwidth request
        {1, 1, 100}, // Self-loop with large bandwidth
        {2, 3, 1}   // Exact capacity match
    };
    
    REQUIRE(network_optimize::can_route_all(N, edges, queries) == true);
}