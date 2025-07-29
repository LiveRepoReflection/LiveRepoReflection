#include <vector>
#include <cassert>
#include "catch.hpp"
#include "route_optim.h"

using namespace route_optim;

TEST_CASE("Empty graph returns no route") {
    // Reset graph to ensure no nodes or edges exist.
    reset();
    
    Route resultCheapest = findCheapestRoute(1, 2, 100);
    Route resultFastest = findFastestRoute(1, 2, 100);
    
    // Expect empty path and zero costs when no route exists.
    CHECK(resultCheapest.path.empty());
    CHECK(resultCheapest.totalMonetaryCost == 0.0);
    CHECK(resultCheapest.totalTimeCost == 0);
    
    CHECK(resultFastest.path.empty());
    CHECK(resultFastest.totalMonetaryCost == 0.0);
    CHECK(resultFastest.totalTimeCost == 0);
}

TEST_CASE("Source equals destination returns trivial route") {
    reset();
    
    // Add a single node.
    addNode(1, 0.0, 0.0);
    
    Route resultCheapest = findCheapestRoute(1, 1, 50);
    Route resultFastest = findFastestRoute(1, 1, 50);
    
    // The trivial route should contain the single node with zero costs.
    std::vector<int> expectedPath = {1};
    CHECK(resultCheapest.path == expectedPath);
    CHECK(resultCheapest.totalMonetaryCost == 0.0);
    CHECK(resultCheapest.totalTimeCost == 0);
    
    CHECK(resultFastest.path == expectedPath);
    CHECK(resultFastest.totalMonetaryCost == 0.0);
    CHECK(resultFastest.totalTimeCost == 0);
}

TEST_CASE("Direct edge without security zones") {
    reset();
    
    // Set up nodes.
    addNode(1, 0.0, 0.0);
    addNode(2, 1.0, 1.0);
    
    // Add a direct edge from 1 to 2.
    addEdge(1, 2, 10.0, 5);
    
    Route resultCheapest = findCheapestRoute(1, 2, 200);
    Route resultFastest = findFastestRoute(1, 2, 200);
    
    std::vector<int> expectedPath = {1, 2};
    CHECK(resultCheapest.path == expectedPath);
    CHECK(resultCheapest.totalMonetaryCost == Approx(10.0));
    CHECK(resultCheapest.totalTimeCost == 5);
    
    CHECK(resultFastest.path == expectedPath);
    CHECK(resultFastest.totalMonetaryCost == Approx(10.0));
    CHECK(resultFastest.totalTimeCost == 5);
}

TEST_CASE("Multiple routes with distinct costs: Cheapest vs Fastest") {
    reset();
    
    // Create nodes.
    addNode(1, 0.0, 0.0);
    addNode(2, 1.0, 1.0);
    addNode(3, 2.0, 2.0);
    addNode(4, 3.0, 3.0);
    
    // Construct graph with two paths from 1 to 4:
    // Path A: 1 -> 2 -> 4: Monetary cost = 5 + 5 = 10, Time cost = 10 + 10 = 20.
    // Path B: 1 -> 3 -> 4: Monetary cost = 8 + 8 = 16, Time cost = 5 + 5 = 10.
    addEdge(1, 2, 5.0, 10);
    addEdge(2, 4, 5.0, 10);
    addEdge(1, 3, 8.0, 5);
    addEdge(3, 4, 8.0, 5);
    
    Route cheapest = findCheapestRoute(1, 4, 300);
    Route fastest = findFastestRoute(1, 4, 300);
    
    std::vector<int> expectedCheapest = {1, 2, 4};
    std::vector<int> expectedFastest = {1, 3, 4};
    
    CHECK(cheapest.path == expectedCheapest);
    CHECK(cheapest.totalMonetaryCost == Approx(10.0));
    CHECK(cheapest.totalTimeCost == 20);
    
    CHECK(fastest.path == expectedFastest);
    CHECK(fastest.totalMonetaryCost == Approx(16.0));
    CHECK(fastest.totalTimeCost == 10);
}

TEST_CASE("Route through security zones with dynamic penalty") {
    reset();
    
    // Create a graph where security zones affect the route.
    // Nodes: 1 -> 2 -> 3 -> 4
    addNode(1, 0.0, 0.0);
    addNode(2, 1.0, 0.0);
    addNode(3, 2.0, 0.0);
    addNode(4, 3.0, 0.0);
    
    // Add edges.
    addEdge(1, 2, 2.0, 5);
    addEdge(2, 3, 2.0, 5);
    addEdge(3, 4, 2.0, 5);
    
    // Also add a direct edge 1 -> 4 bypassing security zones.
    addEdge(1, 4, 10.0, 20);
    
    // Mark node 2 and 3 as security zones for time period 100 to 200 with a penalty.
    addSecurityZone(2, 100, 200, 3.0, 2);
    addSecurityZone(3, 100, 200, 3.0, 2);
    
    // At time 150, security zones are active.
    Route cheapestAtPenalty = findCheapestRoute(1, 4, 150);
    Route fastestAtPenalty = findFastestRoute(1, 4, 150);
    
    // For the lower cost route (1->2->3->4):
    // Monetary: 2+2+2 + penalty on node2 and node3: 3+3 = 12.
    // Time: 5+5+5 + penalty: 2+2 = 19.
    // Direct edge: monetary 10.0, time 20.
    // Thus, for cheapest route, direct edge is cost 10 vs 12.
    std::vector<int> expectedCheapest = {1, 4};
    CHECK(cheapestAtPenalty.path == expectedCheapest);
    CHECK(cheapestAtPenalty.totalMonetaryCost == Approx(10.0));
    CHECK(cheapestAtPenalty.totalTimeCost == 20);
    
    // For the fastest route, lower time is via the multi-edge path: 19 vs 20.
    std::vector<int> expectedFastest = {1, 2, 3, 4};
    CHECK(fastestAtPenalty.path == expectedFastest);
    CHECK(fastestAtPenalty.totalMonetaryCost == Approx(12.0));
    CHECK(fastestAtPenalty.totalTimeCost == 19);
    
    // Now simulate a dynamic update where the penalty is reduced for nodes 2 and 3 at a later time.
    updateSecurityZone(2, 100, 200, 0.0, 0);
    updateSecurityZone(3, 100, 200, 0.0, 0);
    
    // At time 150 again, recalculate routes.
    Route cheapestAfterUpdate = findCheapestRoute(1, 4, 150);
    Route fastestAfterUpdate = findFastestRoute(1, 4, 150);
    
    // Now, the multi-edge path: Monetary: 2+2+2 = 6, Time: 5+5+5 = 15.
    // Direct edge: Monetary: 10, Time: 20.
    std::vector<int> expectedMultiEdge = {1, 2, 3, 4};
    CHECK(cheapestAfterUpdate.path == expectedMultiEdge);
    CHECK(cheapestAfterUpdate.totalMonetaryCost == Approx(6.0));
    CHECK(cheapestAfterUpdate.totalTimeCost == 15);
    
    CHECK(fastestAfterUpdate.path == expectedMultiEdge);
    CHECK(fastestAfterUpdate.totalMonetaryCost == Approx(6.0));
    CHECK(fastestAfterUpdate.totalTimeCost == 15);
}

TEST_CASE("Graph with multiple valid routes and no connectivity") {
    reset();
    
    // Create nodes where some nodes are isolated.
    addNode(1, 0.0, 0.0);
    addNode(2, 1.0, 1.0);
    addNode(3, 2.0, 2.0);
    addNode(4, 3.0, 3.0);
    addNode(5, 4.0, 4.0);
    
    // Connect some nodes.
    addEdge(1, 2, 4.0, 8);
    addEdge(2, 3, 4.0, 8);
    addEdge(3, 4, 4.0, 8);
    
    // Node 5 remains isolated.
    Route routeToIsolatedCheapest = findCheapestRoute(1, 5, 250);
    Route routeToIsolatedFastest = findFastestRoute(1, 5, 250);
    
    // Expect no route found.
    CHECK(routeToIsolatedCheapest.path.empty());
    CHECK(routeToIsolatedCheapest.totalMonetaryCost == 0.0);
    CHECK(routeToIsolatedCheapest.totalTimeCost == 0);
    
    CHECK(routeToIsolatedFastest.path.empty());
    CHECK(routeToIsolatedFastest.totalMonetaryCost == 0.0);
    CHECK(routeToIsolatedFastest.totalTimeCost == 0);
}