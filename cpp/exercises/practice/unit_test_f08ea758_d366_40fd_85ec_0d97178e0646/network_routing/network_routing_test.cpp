#include "network_routing.h"
#include "catch.hpp"
#include <vector>
#include <utility>

TEST_CASE("Basic graph initialization", "[graph_init]") {
    NetworkRouting nr;
    std::vector<std::pair<std::pair<int, int>, int>> edges = {
        {{0, 1}, 10},
        {{0, 2}, 5},
        {{1, 2}, 2},
        {{1, 3}, 1},
        {{2, 3}, 4}
    };
    nr.initialize(4, edges);
    
    SECTION("Initial shortest path check") {
        REQUIRE(nr.query(0, 0, 0) == 0);
        REQUIRE(nr.query(0, 0, 3) == 8); // 0->2->1->3 (5+2+1)
    }
}

TEST_CASE("Single update operation", "[single_update]") {
    NetworkRouting nr;
    std::vector<std::pair<std::pair<int, int>, int>> edges = {
        {{0, 1}, 10},
        {{0, 2}, 5}
    };
    nr.initialize(3, edges);
    
    nr.process_update(1, 0, 1, 15);
    
    SECTION("Query before update timestamp") {
        REQUIRE(nr.query(0, 0, 1) == 10);
    }
    
    SECTION("Query after update timestamp") {
        REQUIRE(nr.query(2, 0, 1) == 15);
    }
}

TEST_CASE("Multiple updates and queries", "[multiple_operations]") {
    NetworkRouting nr;
    std::vector<std::pair<std::pair<int, int>, int>> edges = {
        {{0, 1}, 10},
        {{0, 2}, 5},
        {{1, 2}, 2},
        {{1, 3}, 1},
        {{2, 3}, 4}
    };
    nr.initialize(4, edges);
    
    nr.process_update(1, 0, 1, 15);
    nr.process_update(2, 1, 3, 3);
    nr.process_update(3, 0, 2, 8);
    
    SECTION("Query at timestamp 2") {
        REQUIRE(nr.query(2, 0, 3) == 9); // 0->2->3 (5+4)
    }
    
    SECTION("Query at timestamp 3") {
        REQUIRE(nr.query(3, 0, 3) == 12); // 0->2->3 (8+4)
    }
    
    SECTION("Query non-existent path") {
        REQUIRE(nr.query(3, 0, 4) == -1);
    }
}

TEST_CASE("Edge case: single node", "[single_node]") {
    NetworkRouting nr;
    std::vector<std::pair<std::pair<int, int>, int>> edges;
    nr.initialize(1, edges);
    
    SECTION("Query same node") {
        REQUIRE(nr.query(0, 0, 0) == 0);
    }
    
    SECTION("Query invalid node") {
        REQUIRE(nr.query(0, 0, 1) == -1);
    }
}

TEST_CASE("Performance test with many updates", "[performance]") {
    NetworkRouting nr;
    std::vector<std::pair<std::pair<int, int>, int>> edges = {
        {{0, 1}, 1},
        {{1, 2}, 1},
        {{2, 3}, 1}
    };
    nr.initialize(4, edges);
    
    for (int i = 1; i <= 1000; ++i) {
        nr.process_update(i, (i-1)%3, i%3, i%10 + 1);
    }
    
    SECTION("Query after many updates") {
        REQUIRE(nr.query(1000, 0, 3) > 0);
    }
}