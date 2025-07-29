#include "network_path.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

TEST_CASE("Basic path finding", "[basic]") {
    std::vector<std::tuple<int, int, int, int>> connections = {
        {0, 1, 5, 10},
        {0, 2, 10, 5},
        {1, 2, 2, 8},
        {1, 3, 8, 12},
        {2, 3, 5, 7},
        {3, 4, 3, 15}
    };
    
    SECTION("Simple path with bandwidth requirement") {
        std::vector<int> expected = {0, 1, 3, 4};
        REQUIRE(find_optimal_path(5, connections, 0, 4, 8) == expected);
    }
}

TEST_CASE("Edge cases", "[edge]") {
    SECTION("Empty connections") {
        std::vector<std::tuple<int, int, int, int>> connections;
        std::vector<int> expected;
        REQUIRE(find_optimal_path(5, connections, 0, 4, 8) == expected);
    }

    SECTION("Start and end nodes are the same") {
        std::vector<std::tuple<int, int, int, int>> connections = {{0, 1, 5, 10}};
        std::vector<int> expected = {2};
        REQUIRE(find_optimal_path(3, connections, 2, 2, 8) == expected);
    }

    SECTION("Invalid node indices") {
        std::vector<std::tuple<int, int, int, int>> connections = {{0, 1, 5, 10}};
        std::vector<int> expected;
        REQUIRE(find_optimal_path(2, connections, 0, 5, 8) == expected);
    }
}

TEST_CASE("Complex network scenarios", "[complex]") {
    SECTION("Multiple possible paths") {
        std::vector<std::tuple<int, int, int, int>> connections = {
            {0, 1, 5, 10},
            {1, 2, 5, 10},
            {0, 3, 3, 10},
            {3, 4, 3, 10},
            {4, 2, 3, 10}
        };
        // Should choose path with minimum total latency
        std::vector<int> expected = {0, 3, 4, 2};
        REQUIRE(find_optimal_path(5, connections, 0, 2, 8) == expected);
    }

    SECTION("No valid path due to bandwidth constraints") {
        std::vector<std::tuple<int, int, int, int>> connections = {
            {0, 1, 5, 7},
            {1, 2, 5, 7},
            {2, 3, 5, 7}
        };
        std::vector<int> expected;
        REQUIRE(find_optimal_path(4, connections, 0, 3, 8) == expected);
    }
}

TEST_CASE("Large network test", "[performance]") {
    std::vector<std::tuple<int, int, int, int>> connections;
    // Create a chain of nodes from 0 to 999
    for (int i = 0; i < 999; ++i) {
        connections.push_back({i, i + 1, 1, 10});
    }
    
    SECTION("Long path finding") {
        std::vector<int> expected;
        for (int i = 0; i <= 999; ++i) {
            expected.push_back(i);
        }
        REQUIRE(find_optimal_path(1000, connections, 0, 999, 8) == expected);
    }
}

TEST_CASE("Multiple connections between same nodes", "[multiple]") {
    std::vector<std::tuple<int, int, int, int>> connections = {
        {0, 1, 5, 10},
        {0, 1, 3, 8},
        {0, 1, 2, 5},
        {1, 2, 4, 12}
    };
    
    SECTION("Choose best connection") {
        std::vector<int> expected = {0, 1, 2};
        REQUIRE(find_optimal_path(3, connections, 0, 2, 8) == expected);
    }
}

TEST_CASE("Cyclic paths", "[cycles]") {
    std::vector<std::tuple<int, int, int, int>> connections = {
        {0, 1, 5, 10},
        {1, 2, 5, 10},
        {2, 0, 5, 10},
        {0, 3, 15, 20}
    };
    
    SECTION("Direct path vs cyclic path") {
        std::vector<int> expected = {0, 3};
        REQUIRE(find_optimal_path(4, connections, 0, 3, 8) == expected);
    }
}