#include "network_routing.h"
#include "catch.hpp"
#include <vector>

TEST_CASE("Basic path finding") {
    NetworkRouter router(5); // 5 nodes

    SECTION("Single direct path") {
        router.add_link(0, 1, 5);
        std::vector<int> expected = {0, 1};
        REQUIRE(router.get_optimal_path(0, 1) == expected);
    }

    SECTION("Path through intermediate node") {
        router.add_link(0, 1, 5);
        router.add_link(1, 2, 3);
        std::vector<int> expected = {0, 1, 2};
        REQUIRE(router.get_optimal_path(0, 2) == expected);
    }

    SECTION("Choose shortest of multiple paths") {
        router.add_link(0, 1, 5);
        router.add_link(1, 2, 3);
        router.add_link(0, 2, 10);
        std::vector<int> expected = {0, 1, 2}; // Cost 8 is better than direct cost 10
        REQUIRE(router.get_optimal_path(0, 2) == expected);
    }
}

TEST_CASE("Link modifications") {
    NetworkRouter router(5);

    SECTION("Update existing link") {
        router.add_link(0, 1, 5);
        router.add_link(0, 1, 3); // Update cost
        std::vector<int> expected = {0, 1};
        REQUIRE(router.get_optimal_path(0, 1) == expected);
    }

    SECTION("Remove link and find alternative") {
        router.add_link(0, 1, 5);
        router.add_link(1, 2, 3);
        router.add_link(0, 2, 10);
        router.remove_link(1, 2);
        std::vector<int> expected = {0, 2}; // Only direct path remains
        REQUIRE(router.get_optimal_path(0, 2) == expected);
    }
}

TEST_CASE("Edge cases") {
    NetworkRouter router(5);

    SECTION("No path exists") {
        router.add_link(0, 1, 5);
        router.add_link(2, 3, 3);
        REQUIRE(router.get_optimal_path(0, 3).empty());
    }

    SECTION("Path to self") {
        router.add_link(0, 1, 5);
        std::vector<int> expected = {0};
        REQUIRE(router.get_optimal_path(0, 0) == expected);
    }

    SECTION("Disconnected graph") {
        router.add_link(0, 1, 5);
        router.add_link(2, 3, 3);
        router.remove_link(0, 1);
        REQUIRE(router.get_optimal_path(0, 1).empty());
    }
}

TEST_CASE("Complex scenarios") {
    NetworkRouter router(6);

    SECTION("Multiple possible paths") {
        router.add_link(0, 1, 2);
        router.add_link(1, 2, 2);
        router.add_link(2, 3, 2);
        router.add_link(0, 4, 1);
        router.add_link(4, 5, 1);
        router.add_link(5, 3, 1);
        std::vector<int> expected = {0, 4, 5, 3}; // Should choose path with total cost 3 over path with total cost 6
        REQUIRE(router.get_optimal_path(0, 3) == expected);
    }

    SECTION("Dynamic path updates") {
        router.add_link(0, 1, 2);
        router.add_link(1, 2, 2);
        router.add_link(0, 2, 5);
        
        std::vector<int> expected1 = {0, 1, 2};
        REQUIRE(router.get_optimal_path(0, 2) == expected1);
        
        router.remove_link(1, 2);
        std::vector<int> expected2 = {0, 2};
        REQUIRE(router.get_optimal_path(0, 2) == expected2);
        
        router.add_link(1, 2, 1);
        std::vector<int> expected3 = {0, 1, 2};
        REQUIRE(router.get_optimal_path(0, 2) == expected3);
    }
}

TEST_CASE("Stress test") {
    NetworkRouter router(1000);
    
    // Create a long chain of nodes
    for (int i = 0; i < 999; i++) {
        router.add_link(i, i + 1, 1);
    }
    
    std::vector<int> expected;
    for (int i = 0; i <= 999; i++) {
        expected.push_back(i);
    }
    
    REQUIRE(router.get_optimal_path(0, 999) == expected);
}