#include "catch.hpp"
#include "network_routing.h"
#include <vector>
#include <string>

TEST_CASE("Basic network with single path") {
    NetworkRouter router(3, {
        {1, 2, 5},
        {2, 3, 5}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 3, updates) == 10);
}

TEST_CASE("Network with multiple possible paths") {
    NetworkRouter router(4, {
        {1, 2, 1},
        {2, 4, 4},
        {1, 3, 2},
        {3, 4, 1}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 4, updates) == 3);
}

TEST_CASE("Network with updates") {
    NetworkRouter router(3, {
        {1, 2, 5},
        {2, 3, 5}
    });
    
    std::vector<Update> updates = {
        {1, 2, 1},
        {2, 3, 1}
    };
    REQUIRE(router.findOptimalPath(1, 3, updates) == 2);
}

TEST_CASE("Disconnected nodes") {
    NetworkRouter router(4, {
        {1, 2, 1},
        {3, 4, 1}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 4, updates) == -1);
}

TEST_CASE("Same source and destination") {
    NetworkRouter router(3, {
        {1, 2, 5},
        {2, 3, 5}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 1, updates) == 0);
}

TEST_CASE("Multiple updates changing optimal path") {
    NetworkRouter router(4, {
        {1, 2, 1},
        {2, 4, 4},
        {1, 3, 2},
        {3, 4, 2}
    });
    
    std::vector<Update> updates = {
        {2, 4, 1},
        {3, 4, 5}
    };
    REQUIRE(router.findOptimalPath(1, 4, updates) == 2);
}

TEST_CASE("Large network stress test") {
    std::vector<Link> links;
    for(int i = 1; i < 100; i++) {
        links.push_back({i, i+1, 1});
    }
    NetworkRouter router(100, links);
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 100, updates) == 99);
}

TEST_CASE("Multiple paths with same total cost") {
    NetworkRouter router(4, {
        {1, 2, 2},
        {2, 4, 2},
        {1, 3, 1},
        {3, 4, 3}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 4, updates) == 4);
}

TEST_CASE("Updates creating new optimal path") {
    NetworkRouter router(4, {
        {1, 2, 10},
        {2, 4, 10},
        {1, 3, 10},
        {3, 4, 10}
    });
    
    std::vector<Update> updates = {
        {1, 3, 1},
        {3, 4, 1}
    };
    REQUIRE(router.findOptimalPath(1, 4, updates) == 2);
}

TEST_CASE("Network with cyclic paths") {
    NetworkRouter router(4, {
        {1, 2, 1},
        {2, 3, 1},
        {3, 4, 1},
        {4, 1, 1}
    });
    
    std::vector<Update> updates = {};
    REQUIRE(router.findOptimalPath(1, 3, updates) == 2);
}