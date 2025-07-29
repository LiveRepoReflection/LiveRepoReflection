#include "network_flow.h"
#include "catch.hpp"
#include <vector>
#include <tuple>

using std::vector;
using std::tuple;

TEST_CASE("Basic full allocation", "[network_flow]") {
    // Network: 4 nodes, 4 edges
    // Edges: (0,1,10), (1,2,5), (0,2,15), (2,3,8)
    int N = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 5},
        {0, 2, 15},
        {2, 3, 8}
    };
    network_flow::init_network(N, edges);
    
    // Add a request from 0 to 3 with demand 7.
    // Expected allocation should be 7 if there exists a feasible routing.
    network_flow::add_request(0, 0, 3, 7);
    int allocation = network_flow::query_request(0);
    REQUIRE(allocation == 7);
}

TEST_CASE("Partial allocation due to capacity limits", "[network_flow]") {
    // Network: 3 nodes, 2 edges
    // Edges: (0,1,3), (1,2,3)
    int N = 3;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 3},
        {1, 2, 3}
    };
    network_flow::init_network(N, edges);
    
    // Request from 0 to 2 with demand 5, but the maximum flow available is 3.
    network_flow::add_request(1, 0, 2, 5);
    int allocation = network_flow::query_request(1);
    REQUIRE(allocation == 3);
}

TEST_CASE("Request removal", "[network_flow]") {
    // Network: 4 nodes, same as in the basic test.
    int N = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 5},
        {0, 2, 15},
        {2, 3, 8}
    };
    network_flow::init_network(N, edges);
    
    network_flow::add_request(2, 0, 3, 7);
    int allocation_before = network_flow::query_request(2);
    REQUIRE(allocation_before == 7);
    network_flow::remove_request(2);
    int allocation_after = network_flow::query_request(2);
    REQUIRE(allocation_after == 0);
}

TEST_CASE("Concurrent Requests with shared edges", "[network_flow]") {
    // Network: 5 nodes, 6 edges
    // Edges: (0,1,10), (1,2,10), (0,3,10), (3,4,10), (1,4,5), (2,4,10)
    int N = 5;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 10},
        {0, 3, 10},
        {3, 4, 10},
        {1, 4, 5},
        {2, 4, 10}
    };
    network_flow::init_network(N, edges);
    
    // Add two requests:
    // Request 3: from 0 to 4 with demand 12.
    // Request 4: from 0 to 2 with demand 8.
    network_flow::add_request(3, 0, 4, 12);
    network_flow::add_request(4, 0, 2, 8);
    
    int allocation3 = network_flow::query_request(3);
    int allocation4 = network_flow::query_request(4);
    // Expected allocations as determined by the network flow solution.
    // Here we assume that the algorithm is capable of allocating the full
    // demanded bandwidth when possible.
    REQUIRE(allocation3 == 12);
    REQUIRE(allocation4 == 8);
}

TEST_CASE("Multiple operations and re-adding requests", "[network_flow]") {
    // Network: 6 nodes, 7 edges
    // Edges: (0,1,10), (1,2,10), (2,3,10), (3,4,10), (4,5,10), (0,5,5), (1,4,5)
    int N = 6;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10},
        {1, 2, 10},
        {2, 3, 10},
        {3, 4, 10},
        {4, 5, 10},
        {0, 5, 5},
        {1, 4, 5}
    };
    network_flow::init_network(N, edges);
    
    // Add request 5 from 0 to 5 with demand 10.
    network_flow::add_request(5, 0, 5, 10);
    int allocation5 = network_flow::query_request(5);
    REQUIRE(allocation5 == 10);
    
    // Remove request 5.
    network_flow::remove_request(5);
    int allocation_removed = network_flow::query_request(5);
    REQUIRE(allocation_removed == 0);
    
    // Add request 6 from 1 to 3 with demand 7.
    network_flow::add_request(6, 1, 3, 7);
    int allocation6 = network_flow::query_request(6);
    REQUIRE(allocation6 == 7);
    
    // Add request 7 from 2 to 4 with demand 8.
    network_flow::add_request(7, 2, 4, 8);
    int allocation7 = network_flow::query_request(7);
    REQUIRE(allocation7 == 8);
    
    // Remove request 6.
    network_flow::remove_request(6);
    int allocation6_removed = network_flow::query_request(6);
    REQUIRE(allocation6_removed == 0);
    
    // Re-add request 5 from 0 to 5 with demand 6.
    network_flow::add_request(5, 0, 5, 6);
    int allocation5_readded = network_flow::query_request(5);
    REQUIRE(allocation5_readded == 6);
}