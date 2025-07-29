#include <sstream>
#include <string>
#include <vector>
#include "catch.hpp"
#include "network_routing.h"

TEST_CASE("Simple connected graph routing") {
    // Graph:
    // 1 -1- 2 -2- 3 -3- 4
    // 1 --10-- 4
    // Q: 3 routing requests.
    std::string input_data = 
        "4 4\n"         // N = 4 nodes, M = 4 edges
        "1 2 1\n"       // Edge from 1 to 2 with latency 1
        "2 3 2\n"       // Edge from 2 to 3 with latency 2
        "3 4 3\n"       // Edge from 3 to 4 with latency 3
        "1 4 10\n"      // Edge from 1 to 4 with latency 10
        "3\n"           // Q = 3 routing requests
        "1 4\n"         // Request 1: from node 1 to 4 (shortest path: 1->2->3->4 = 6)
        "1 3\n"         // Request 2: from node 1 to 3 (shortest path: 1->2->3 = 3)
        "2 4\n";        // Request 3: from node 2 to 4 (shortest path: 2->3->4 = 5)

    std::istringstream iss(input_data);
    std::ostringstream oss;
    
    network_routing::solve(iss, oss);
    
    std::string expected_output = 
        "6\n"
        "3\n"
        "5\n";
        
    REQUIRE(oss.str() == expected_output);
}

TEST_CASE("Disconnected graph: unreachable destination") {
    // Graph:
    // 1 -5- 2 are connected, node 3 is isolated.
    // Q: 2 routing requests.
    std::string input_data =
        "3 1\n"         // N = 3 nodes, M = 1 edge
        "1 2 5\n"       // Edge connecting 1 and 2 with latency 5
        "2\n"           // Q = 2 routing requests
        "1 2\n"         // Request 1: 1 to 2: expected = 5
        "1 3\n";        // Request 2: 1 to 3: expected = -1 (no path)

    std::istringstream iss(input_data);
    std::ostringstream oss;
    
    network_routing::solve(iss, oss);
    
    std::string expected_output =
        "5\n"
        "-1\n";
    
    REQUIRE(oss.str() == expected_output);
}

TEST_CASE("Source and destination are the same") {
    // Graph:
    // Single node, no edges.
    // Q: 1 routing request where source equals destination.
    std::string input_data =
        "1 0\n"         // N = 1 node, M = 0 edges
        "1\n"           // Q = 1 routing request
        "1 1\n";        // Request: 1 to 1, expected cost = 0 since same node

    std::istringstream iss(input_data);
    std::ostringstream oss;
    
    network_routing::solve(iss, oss);
    
    std::string expected_output = "0\n";
    
    REQUIRE(oss.str() == expected_output);
}

TEST_CASE("Multiple routing requests with competing paths") {
    // Graph:
    // 1 -1- 2 -2- 5
    // 1 -2- 3 -2- 4 -1- 5
    // 2 -2- 3 (additional edge)
    // Q: 3 routing requests.
    std::string input_data =
        "5 6\n"         // N = 5 nodes, M = 6 edges
        "1 2 1\n"       // Edge from 1 to 2 (latency = 1)
        "2 5 5\n"       // Edge from 2 to 5 (latency = 5)
        "1 3 2\n"       // Edge from 1 to 3 (latency = 2)
        "3 4 2\n"       // Edge from 3 to 4 (latency = 2)
        "4 5 1\n"       // Edge from 4 to 5 (latency = 1)
        "2 3 2\n"       // Additional edge from 2 to 3 (latency = 2)
        "3\n"           // Q = 3 routing requests
        "1 5\n"         // Request 1: 1 to 5, expected = 5 (1->3->4->5: 2+2+1)
        "2 4\n"         // Request 2: 2 to 4, expected = 4 (2->3->4: 2+2)
        "3 5\n";        // Request 3: 3 to 5, expected = 3 (3->4->5: 2+1)

    std::istringstream iss(input_data);
    std::ostringstream oss;
    
    network_routing::solve(iss, oss);
    
    std::string expected_output =
        "5\n"
        "4\n"
        "3\n";
    
    REQUIRE(oss.str() == expected_output);
}