#include "catch.hpp"
#include "optimal_highway.h"
#include <vector>
#include <tuple>

TEST_CASE("Example case from the problem statement") {
    int N = 4;
    int M = 3;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 10}, {1, 2, 15}}, // Phase 0
        {{2, 3, 20}, {0, 3, 5}},   // Phase 1
        {{1, 3, 12}}               // Phase 2
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 30);
}

TEST_CASE("Connectivity already achieved in first phase") {
    int N = 3;
    int M = 2;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 5}, {1, 2, 10}, {0, 2, 15}}, // Phase 0
        {{0, 1, 2}, {1, 2, 3}}               // Phase 1
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 15);
}

TEST_CASE("Need all phases for connectivity") {
    int N = 5;
    int M = 3;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 3}, {2, 3, 5}},       // Phase 0
        {{1, 2, 10}, {3, 4, 7}},       // Phase 1
        {{0, 4, 20}}                   // Phase 2
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 25);
}

TEST_CASE("Multiple possible combinations to achieve minimum cost") {
    int N = 4;
    int M = 2;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 10}, {1, 2, 5}, {2, 3, 8}},  // Phase 0
        {{0, 3, 7}, {0, 2, 12}}              // Phase 1
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 23);
}

TEST_CASE("Single city case") {
    int N = 1;
    int M = 1;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {}  // Phase 0 - nothing to connect
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 0);
}

TEST_CASE("Two cities case") {
    int N = 2;
    int M = 1;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 42}}  // Phase 0
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 42);
}

TEST_CASE("Large network with multiple phases") {
    int N = 6;
    int M = 3;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 5}, {2, 3, 8}},                    // Phase 0
        {{1, 2, 10}, {3, 4, 7}, {4, 5, 9}},        // Phase 1
        {{0, 5, 15}, {1, 3, 6}, {0, 4, 12}}        // Phase 2
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 39);
}

TEST_CASE("Many redundant edges") {
    int N = 5;
    int M = 2;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 3}, {1, 2, 5}, {2, 3, 2}, {3, 4, 1}, {0, 2, 10}, {0, 3, 15}, {1, 3, 8}, {1, 4, 12}, {2, 4, 7}}, // Phase 0
        {{0, 4, 6}}                                                                                               // Phase 1
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 11);
}

TEST_CASE("Multiple equally optimal solutions") {
    int N = 4;
    int M = 2;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 5}, {1, 2, 5}},       // Phase 0
        {{2, 3, 5}, {0, 3, 5}}        // Phase 1
    };

    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 15);
}

TEST_CASE("Higher cost early connection vs lower cost late connection") {
    int N = 3;
    int M = 2;
    std::vector<std::vector<std::tuple<int, int, int>>> phases = {
        {{0, 1, 100}, {1, 2, 100}},   // Phase 0 - expensive but early
        {{0, 2, 1}}                   // Phase 1 - cheaper but late
    };

    // We must connect as early as possible, so we use phase 0 roads
    REQUIRE(optimal_highway::minimum_cost(N, M, phases) == 200);
}