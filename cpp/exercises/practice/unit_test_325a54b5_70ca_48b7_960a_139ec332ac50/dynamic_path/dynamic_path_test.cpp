#include "dynamic_path.h"
#include "catch.hpp"
#include <vector>
#include <utility>

TEST_CASE("Basic graph with no updates") {
    SECTION("Simple path between two nodes") {
        std::vector<std::vector<int>> edges = {
            {0, 1, 5},
            {1, 2, 3},
            {0, 2, 10}
        };
        DynamicPath graph(3, edges);
        REQUIRE(graph.findShortestPath(0, 2) == 8);
    }
}

TEST_CASE("Graph with edge updates") {
    std::vector<std::vector<int>> edges = {
        {0, 1, 5},
        {1, 2, 3},
        {0, 2, 10}
    };
    DynamicPath graph(3, edges);
    
    SECTION("Update edge and verify new shortest path") {
        graph.updateEdge(0, 1, 2);
        REQUIRE(graph.findShortestPath(0, 2) == 5);
    }
    
    SECTION("Multiple updates on same edge") {
        graph.updateEdge(0, 1, 2);
        graph.updateEdge(0, 1, 7);
        REQUIRE(graph.findShortestPath(0, 2) == 10);
    }
}

TEST_CASE("Large graph operations") {
    std::vector<std::vector<int>> edges = {
        {0, 1, 5}, {1, 2, 3}, {2, 3, 4},
        {3, 4, 2}, {4, 5, 6}, {5, 0, 8},
        {1, 4, 7}, {2, 5, 9}, {0, 3, 12}
    };
    DynamicPath graph(6, edges);
    
    SECTION("Finding path in larger graph") {
        REQUIRE(graph.findShortestPath(0, 4) == 12);
    }
    
    SECTION("Multiple updates and queries") {
        graph.updateEdge(0, 3, 6);
        REQUIRE(graph.findShortestPath(0, 4) == 8);
        graph.updateEdge(1, 4, 3);
        REQUIRE(graph.findShortestPath(0, 4) == 8);
    }
}

TEST_CASE("Edge cases") {
    std::vector<std::vector<int>> edges = {
        {0, 1, 1000000000},
        {1, 2, 1000000000}
    };
    DynamicPath graph(3, edges);
    
    SECTION("Maximum weight edges") {
        REQUIRE(graph.findShortestPath(0, 2) == 2000000000);
    }
    
    SECTION("Same start and end node") {
        REQUIRE(graph.findShortestPath(0, 0) == 0);
    }
}

TEST_CASE("Example from problem statement") {
    std::vector<std::vector<int>> edges = {
        {0, 1, 5}, {0, 2, 2}, {1, 2, 1},
        {1, 3, 3}, {2, 3, 4}, {2, 4, 6},
        {3, 4, 1}
    };
    DynamicPath graph(5, edges);
    
    SECTION("Following example sequence") {
        REQUIRE(graph.findShortestPath(0, 4) == 7);
        graph.updateEdge(1, 2, 2);
        REQUIRE(graph.findShortestPath(0, 4) == 7);
        graph.updateEdge(3, 4, 5);
        REQUIRE(graph.findShortestPath(0, 4) == 8);
    }
}

TEST_CASE("Stress test with many operations") {
    std::vector<std::vector<int>> edges;
    // Create a complete graph with 10 nodes
    for(int i = 0; i < 10; i++) {
        for(int j = i + 1; j < 10; j++) {
            edges.push_back({i, j, (i + j) * 100});
        }
    }
    DynamicPath graph(10, edges);
    
    SECTION("Multiple operations") {
        for(int i = 0; i < 100; i++) {
            int start = i % 10;
            int end = (i + 5) % 10;
            REQUIRE(graph.findShortestPath(start, end) > 0);
            if(i % 3 == 0) {
                graph.updateEdge(i % 10, (i + 1) % 10, i * 50);
            }
        }
    }
}