#include "autonomous_routing.h"
#include "catch.hpp"
#include <vector>

TEST_CASE("Basic single path test", "[basic]") {
    // Create a simple linear graph with 3 nodes
    Graph g(3);
    g.addRoad(0, 1, 10, 1); // length 10, congestion 1
    g.addRoad(1, 2, 10, 1);
    
    std::vector<DeliveryRequest> requests = {
        {0, 2, 100} // from 0 to 2, deadline 100
    };
    
    RoutePlanner planner(g, 1.0, 1.0); // α = 1.0, β = 1.0
    auto result = planner.planRoute(requests[0]);
    
    REQUIRE(result.success == true);
    REQUIRE(result.route == std::vector<int>{0, 1, 2});
    REQUIRE(result.totalCost == 22.0); // (10 + 10) * 1.0 + (1 + 1) * 1.0
}

TEST_CASE("Test with impossible deadline", "[deadline]") {
    Graph g(2);
    g.addRoad(0, 1, 100, 1);
    
    DeliveryRequest request{0, 1, 50}; // deadline too short
    
    RoutePlanner planner(g, 1.0, 1.0);
    auto result = planner.planRoute(request);
    
    REQUIRE(result.success == false);
}

TEST_CASE("Test with multiple possible paths", "[multiple_paths]") {
    Graph g(4);
    // Path 1: 0->1->3 (shorter but more congested)
    g.addRoad(0, 1, 10, 5);
    g.addRoad(1, 3, 10, 5);
    // Path 2: 0->2->3 (longer but less congested)
    g.addRoad(0, 2, 15, 1);
    g.addRoad(2, 3, 15, 1);
    
    DeliveryRequest request{0, 3, 100};
    
    SECTION("Prioritize time over congestion") {
        RoutePlanner planner(g, 1.0, 0.1); // α = 1.0, β = 0.1
        auto result = planner.planRoute(request);
        REQUIRE(result.route == std::vector<int>{0, 1, 3});
    }
    
    SECTION("Prioritize congestion over time") {
        RoutePlanner planner(g, 0.1, 1.0); // α = 0.1, β = 1.0
        auto result = planner.planRoute(request);
        REQUIRE(result.route == std::vector<int>{0, 2, 3});
    }
}

TEST_CASE("Test with real-time updates", "[updates]") {
    Graph g(3);
    g.addRoad(0, 1, 10, 1);
    g.addRoad(1, 2, 10, 1);
    
    DeliveryRequest request{0, 2, 100};
    
    RouteWrapper planner(g, 1.0, 1.0);
    auto result1 = planner.planRoute(request);
    
    // Update congestion on first road
    g.updateCongestion(0, 1, 10);
    
    auto result2 = planner.planRoute(request);
    REQUIRE(result2.totalCost > result1.totalCost);
}

TEST_CASE("Test with disconnected graph", "[disconnected]") {
    Graph g(4);
    g.addRoad(0, 1, 10, 1);
    // No connection to node 2 or 3
    
    DeliveryRequest request{0, 2, 100};
    
    RouteWrapper planner(g, 1.0, 1.0);
    auto result = planner.planRoute(request);
    REQUIRE(result.success == false);
}

TEST_CASE("Test with large graph performance", "[performance]") {
    Graph g(1000);
    // Create a grid-like structure
    for(int i = 0; i < 999; i++) {
        g.addRoad(i, i+1, 10, 1);
        if(i < 900) {
            g.addRoad(i, i+100, 10, 1);
        }
    }
    
    DeliveryRequest request{0, 999, 5000};
    
    RouteWrapper planner(g, 1.0, 1.0);
    auto start = std::chrono::high_resolution_clock::now();
    auto result = planner.planRoute(request);
    auto end = std::chrono::high_resolution_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    REQUIRE(duration.count() < 1000); // Should complete within 1 second
    REQUIRE(result.success == true);
}

TEST_CASE("Test with extreme congestion values", "[extreme]") {
    Graph g(3);
    g.addRoad(0, 1, 10, 1000000);
    g.addRoad(1, 2, 10, 1000000);
    
    DeliveryRequest request{0, 2, 100};
    
    RouteWrapper planner(g, 1.0, 1.0);
    auto result = planner.planRoute(request);
    REQUIRE(result.success == true);
    REQUIRE(result.totalCost > 2000000);
}