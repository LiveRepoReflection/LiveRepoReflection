#include "network_design.h"
#include "catch.hpp"
#include <vector>
#include <utility>

TEST_CASE("Test basic network throughput calculation", "[network_design]") {
    int N = 4;
    int M = 5;
    std::vector<int> C = {10, 15, 20, 25};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 5},
        {0, 2, 10},
        {1, 2, 8},
        {1, 3, 12},
        {2, 3, 15}
    };
    int T = 100;

    REQUIRE(solve_network_design(N, M, C, connections, T) == 35);
}

TEST_CASE("Test empty network", "[network_design]") {
    int N = 3;
    int M = 0;
    std::vector<int> C = {10, 15, 20};
    std::vector<std::tuple<int, int, int>> connections;
    int T = 10;

    REQUIRE(solve_network_design(N, M, C, connections, T) == -1);
}

TEST_CASE("Test impossible throughput", "[network_design]") {
    int N = 3;
    int M = 3;
    std::vector<int> C = {5, 5, 5};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 1},
        {1, 2, 1},
        {0, 2, 1}
    };
    int T = 1000;

    REQUIRE(solve_network_design(N, M, C, connections, T) == -1);
}

TEST_CASE("Test single connection network", "[network_design]") {
    int N = 2;
    int M = 1;
    std::vector<int> C = {10, 10};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 5}
    };
    int T = 10;

    REQUIRE(solve_network_design(N, M, C, connections, T) == 5);
}

TEST_CASE("Test multiple possible solutions", "[network_design]") {
    int N = 3;
    int M = 3;
    std::vector<int> C = {10, 10, 10};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 5},
        {1, 2, 5},
        {0, 2, 8}
    };
    int T = 20;

    REQUIRE(solve_network_design(N, M, C, connections, T) == 10);
}

TEST_CASE("Test maximum size input", "[network_design]") {
    int N = 50;
    std::vector<int> C(N, 1000000);
    int M = (N * (N-1)) / 2;
    std::vector<std::tuple<int, int, int>> connections;
    
    for(int i = 0; i < N; i++) {
        for(int j = i+1; j < N; j++) {
            connections.push_back({i, j, 1000000});
        }
    }
    int T = 1000000;

    REQUIRE(solve_network_design(N, M, C, connections, T) >= 0);
}

TEST_CASE("Test disconnected components requirement", "[network_design]") {
    int N = 4;
    int M = 2;
    std::vector<int> C = {10, 10, 10, 10};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 5},
        {2, 3, 5}
    };
    int T = 30;

    REQUIRE(solve_network_design(N, M, C, connections, T) == -1);
}

TEST_CASE("Test minimum capacity bottleneck", "[network_design]") {
    int N = 3;
    int M = 2;
    std::vector<int> C = {5, 100, 5};
    std::vector<std::tuple<int, int, int>> connections = {
        {0, 1, 10},
        {1, 2, 10}
    };
    int T = 10;

    REQUIRE(solve_network_design(N, M, C, connections, T) == 20);
}