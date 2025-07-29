#include "network_routing.h"
#include "catch.hpp"
#include <vector>
#include <algorithm>

using std::vector;
using std::tuple;

TEST_CASE("Initial network shortest path", "[network_routing]") {
    // Initialize network with 4 nodes and 3 edges.
    init(4, { {0, 1, 5}, {1, 2, 3}, {2, 3, 2} });
    
    // At timestamp 10, the only available path from 0 to 3 is: 0 -> 1 -> 2 -> 3
    vector<int> expected_path = {0, 1, 2, 3};
    auto result_path = find_shortest_path(0, 3, 10);
    REQUIRE(result_path == expected_path);
    
    // For same start and end node, the path should be a single node.
    vector<int> expected_same_node = {2};
    auto self_path = find_shortest_path(2, 2, 10);
    REQUIRE(self_path == expected_same_node);
}

TEST_CASE("Network update impacts routing", "[network_routing]") {
    // Set up a network with 4 nodes.
    init(4, { {0, 1, 5}, {1, 2, 3}, {2, 3, 2} });
    
    // Initial state at timestamp 10: path 0 -> 1 -> 2 -> 3 with cost 5+3+2 = 10.
    vector<int> expected_initial = {0, 1, 2, 3};
    auto initial_path = find_shortest_path(0, 3, 10);
    REQUIRE(initial_path == expected_initial);
    
    // Update the latency between nodes 1 and 2 to 1 at timestamp 20.
    update_latency(1, 2, 1);
    
    // At timestamp 30, the updated path 0 -> 1 -> 2 -> 3 should reflect the new latency.
    vector<int> expected_updated = {0, 1, 2, 3};
    auto updated_path = find_shortest_path(0, 3, 30);
    REQUIRE(updated_path == expected_updated);
    
    // Remove the link between nodes 2 and 3 at timestamp 40.
    update_latency(2, 3, -1);
    
    // At timestamp 50, there should be no valid path from 0 to 3.
    vector<int> empty_path;
    auto removed_path = find_shortest_path(0, 3, 50);
    REQUIRE(removed_path == empty_path);
}

TEST_CASE("Multiple updates and historical queries", "[network_routing]") {
    // Initialize a network with 5 nodes.
    init(5, { {0, 1, 10}, {1, 2, 5}, {0, 3, 2}, {3, 4, 2}, {4, 2, 2} });
    
    // At timestamp 10, the optimal path from 0 to 2 should be via 0->3->4->2 with cost 2+2+2 = 6,
    // which is better than the direct route 0->1->2 (cost 10+5 = 15).
    vector<int> expected_path1 = {0, 3, 4, 2};
    auto path1 = find_shortest_path(0, 2, 10);
    REQUIRE(path1 == expected_path1);
    
    // At timestamp 20, update the latency of link 0->1 to 1.
    update_latency(0, 1, 1);
    
    // At timestamp 30, there are now two possible paths from 0 to 2:
    // Path A: 0 -> 1 -> 2 with cost 1+5 = 6, or
    // Path B: 0 -> 3 -> 4 -> 2 with cost 2+2+2 = 6.
    // Accept either valid path.
    auto path2 = find_shortest_path(0, 2, 30);
    vector<int> expected_pathA = {0, 1, 2};
    vector<int> expected_pathB = {0, 3, 4, 2};
    bool valid = (path2 == expected_pathA || path2 == expected_pathB);
    REQUIRE(valid);
    
    // At timestamp 40, remove the link between nodes 3 and 4.
    update_latency(3, 4, -1);
    
    // At timestamp 50, the only valid path from 0 to 2 is now: 0 -> 1 -> 2.
    vector<int> expected_path3 = {0, 1, 2};
    auto path3 = find_shortest_path(0, 2, 50);
    REQUIRE(path3 == expected_path3);
}