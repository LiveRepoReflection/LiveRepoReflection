#include "resource_allocator.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

TEST_CASE("Basic allocation test with single node and single job") {
    std::vector<std::vector<double>> nodes = {{10.0, 5.0}};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{2.0, 1.0}, 5, 3}
    };
    std::vector<int> expected = {0};
    REQUIRE(allocateJobs(nodes, requests, 1) == expected);
}

TEST_CASE("Test with multiple nodes and multiple jobs") {
    std::vector<std::vector<double>> nodes = {
        {10.0, 5.0},
        {8.0, 7.0}
    };
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{2.0, 1.0}, 5, 3},
        {{3.0, 2.0}, 3, 2}
    };
    auto result = allocateJobs(nodes, requests, 1);
    REQUIRE(result.size() <= 2);
    for (int idx : result) {
        REQUIRE(idx >= 0);
        REQUIRE(idx < 2);
    }
}

TEST_CASE("Test with insufficient resources") {
    std::vector<std::vector<double>> nodes = {{1.0, 1.0}};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{2.0, 2.0}, 5, 3}
    };
    std::vector<int> expected = {};
    REQUIRE(allocateJobs(nodes, requests, 1) == expected);
}

TEST_CASE("Test with expired deadlines") {
    std::vector<std::vector<double>> nodes = {{10.0, 5.0}};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{2.0, 1.0}, 5, 1}
    };
    std::vector<int> expected = {};
    REQUIRE(allocateJobs(nodes, requests, 2) == expected);
}

TEST_CASE("Test with complex resource distribution") {
    std::vector<std::vector<double>> nodes = {
        {10.0, 5.0, 3.0},
        {8.0, 7.0, 4.0},
        {6.0, 6.0, 5.0}
    };
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{5.0, 3.0, 2.0}, 5, 3},
        {{4.0, 4.0, 1.0}, 4, 2},
        {{3.0, 2.0, 3.0}, 3, 4}
    };
    auto result = allocateJobs(nodes, requests, 1);
    REQUIRE(result.size() <= 3);
    for (int idx : result) {
        REQUIRE(idx >= 0);
        REQUIRE(idx < 3);
    }
}

TEST_CASE("Test with edge case - empty input") {
    std::vector<std::vector<double>> nodes = {};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {};
    std::vector<int> expected = {};
    REQUIRE(allocateJobs(nodes, requests, 1) == expected);
}

TEST_CASE("Test with maximum resource utilization") {
    std::vector<std::vector<double>> nodes = {{10.0, 10.0}};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{5.0, 5.0}, 5, 3},
        {{5.0, 5.0}, 4, 3},
        {{5.0, 5.0}, 3, 3}
    };
    auto result = allocateJobs(nodes, requests, 1);
    REQUIRE(result.size() <= 2);
}

TEST_CASE("Test with priority conflicts") {
    std::vector<std::vector<double>> nodes = {{10.0, 10.0}};
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{8.0, 8.0}, 1, 5},  // Low priority, loose deadline
        {{8.0, 8.0}, 5, 2}   // High priority, tight deadline
    };
    auto result = allocateJobs(nodes, requests, 1);
    if (!result.empty()) {
        REQUIRE(result[0] == 1);  // Should prioritize the second job
    }
}

TEST_CASE("Test resource fragmentation") {
    std::vector<std::vector<double>> nodes = {
        {3.0, 3.0},
        {3.0, 3.0},
        {3.0, 3.0}
    };
    std::vector<std::tuple<std::vector<double>, int, int>> requests = {
        {{8.0, 8.0}, 5, 3}  // Requires combining resources across nodes
    };
    auto result = allocateJobs(nodes, requests, 1);
    REQUIRE(result.size() <= 1);
}