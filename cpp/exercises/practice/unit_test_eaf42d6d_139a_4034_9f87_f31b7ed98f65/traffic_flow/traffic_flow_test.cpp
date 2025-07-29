#include "traffic_flow.h"
#include "catch.hpp"
#include <vector>

TEST_CASE("Basic test with small network - possible flow") {
    int N = 4, M = 5, K = 2;
    std::vector<int> C = {50, 60, 70, 80};  // intersection capacities
    
    std::vector<int> U = {0, 0, 1, 2, 1};   // source intersections
    std::vector<int> V = {1, 2, 3, 3, 2};   // destination intersections
    std::vector<int> L = {10, 5, 15, 10, 5}; // road lengths
    std::vector<int> R = {20, 15, 25, 30, 10}; // road capacities
    
    std::vector<int> S = {0, 2};    // commuter sources
    std::vector<int> D = {3, 3};    // commuter destinations
    std::vector<int> T = {10, 15};  // traffic demands
    std::vector<int> A = {50, 70};  // max acceptable times

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == true);
}

TEST_CASE("Network with impossible flow due to capacity constraints") {
    int N = 3, M = 2, K = 1;
    std::vector<int> C = {10, 10, 10};
    std::vector<int> U = {0, 1};
    std::vector<int> V = {1, 2};
    std::vector<int> L = {5, 5};
    std::vector<int> R = {5, 5};
    std::vector<int> S = {0};
    std::vector<int> D = {2};
    std::vector<int> T = {10};
    std::vector<int> A = {20};

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == false);
}

TEST_CASE("Network with impossible flow due to time constraints") {
    int N = 4, M = 3, K = 1;
    std::vector<int> C = {100, 100, 100, 100};
    std::vector<int> U = {0, 1, 2};
    std::vector<int> V = {1, 2, 3};
    std::vector<int> L = {50, 50, 50};
    std::vector<int> R = {100, 100, 100};
    std::vector<int> S = {0};
    std::vector<int> D = {3};
    std::vector<int> T = {10};
    std::vector<int> A = {100};  // Time limit too short for path length

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == false);
}

TEST_CASE("Maximum capacity network") {
    int N = 2, M = 1, K = 1;
    std::vector<int> C = {1000, 1000};
    std::vector<int> U = {0};
    std::vector<int> V = {1};
    std::vector<int> L = {1};
    std::vector<int> R = {1000};
    std::vector<int> S = {0};
    std::vector<int> D = {1};
    std::vector<int> T = {100};
    std::vector<int> A = {10};

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == true);
}

TEST_CASE("Multiple commuters with shared paths") {
    int N = 4, M = 4, K = 3;
    std::vector<int> C = {100, 100, 100, 100};
    std::vector<int> U = {0, 0, 1, 2};
    std::vector<int> V = {1, 2, 3, 3};
    std::vector<int> L = {10, 10, 10, 10};
    std::vector<int> R = {50, 50, 50, 50};
    std::vector<int> S = {0, 0, 0};
    std::vector<int> D = {3, 3, 3};
    std::vector<int> T = {20, 20, 20};
    std::vector<int> A = {30, 30, 30};

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == true);
}

TEST_CASE("Edge case with minimum values") {
    int N = 1, M = 0, K = 0;
    std::vector<int> C = {1};
    std::vector<int> U = {};
    std::vector<int> V = {};
    std::vector<int> L = {};
    std::vector<int> R = {};
    std::vector<int> S = {};
    std::vector<int> D = {};
    std::vector<int> T = {};
    std::vector<int> A = {};

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == true);
}

TEST_CASE("Network with no valid paths") {
    int N = 4, M = 3, K = 1;
    std::vector<int> C = {100, 100, 100, 100};
    std::vector<int> U = {0, 1, 2};
    std::vector<int> V = {1, 2, 1}; // No path to node 3
    std::vector<int> L = {10, 10, 10};
    std::vector<int> R = {100, 100, 100};
    std::vector<int> S = {0};
    std::vector<int> D = {3};
    std::vector<int> T = {10};
    std::vector<int> A = {100};

    REQUIRE(traffic_flow::is_flow_possible(N, M, K, C, U, V, L, R, S, D, T, A) == false);
}