#include "dynamic_routes.h"
#include "catch.hpp"

TEST_CASE("Basic test without construction", "[case1]") {
    // Simple graph with 3 nodes, no construction
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {1, 2, 5}
    };
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 15) == 10);
}

TEST_CASE("Test with construction blocking optimal path", "[case2]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {0, 2, 10},
        {1, 2, 5}
    };
    std::vector<std::tuple<int, int, int, int>> construction = {
        {0, 1, 0, 10}
    };
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 15) == 10);
}

TEST_CASE("Test impossible route due to deadline", "[case3]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 10},
        {1, 2, 10}
    };
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 15) == -1);
}

TEST_CASE("Test with multiple possible paths", "[case4]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {1, 3, 5},
        {0, 2, 2},
        {2, 3, 7}
    };
    std::vector<std::tuple<int, int, int, int>> construction = {
        {0, 1, 0, 3}
    };
    DynamicRoutes router(4, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 3, 20) == 9);
}

TEST_CASE("Test with no valid path", "[case5]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {2, 3, 5}
    };
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(4, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 3, 100) == -1);
}

TEST_CASE("Test with complex construction schedule", "[case6]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {1, 2, 5},
        {0, 2, 15}
    };
    std::vector<std::tuple<int, int, int, int>> construction = {
        {0, 1, 0, 10},
        {1, 2, 5, 15},
        {0, 2, 12, 20}
    };
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 25) == 15);
}

TEST_CASE("Test maximum size input", "[case7]") {
    std::vector<std::tuple<int, int, int>> roads;
    for(int i = 0; i < 999; i++) {
        roads.push_back({i, i+1, 1});
    }
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(1000, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 999, 1000) == 999);
}

TEST_CASE("Test with overlapping construction periods", "[case8]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {1, 2, 5},
        {0, 2, 12}
    };
    std::vector<std::tuple<int, int, int, int>> construction = {
        {0, 1, 0, 10},
        {0, 1, 5, 15},
        {1, 2, 8, 20}
    };
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 30) == 12);
}

TEST_CASE("Test with tight deadline", "[case9]") {
    std::vector<std::tuple<int, int, int>> roads = {
        {0, 1, 5},
        {1, 2, 5}
    };
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(3, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 2, 10) == 10);
    REQUIRE(router.findOptimalRoute(0, 2, 9) == -1);
}

TEST_CASE("Test with single node", "[case10]") {
    std::vector<std::tuple<int, int, int>> roads;
    std::vector<std::tuple<int, int, int, int>> construction;
    DynamicRoutes router(1, roads, construction);
    
    REQUIRE(router.findOptimalRoute(0, 0, 10) == 0);
}