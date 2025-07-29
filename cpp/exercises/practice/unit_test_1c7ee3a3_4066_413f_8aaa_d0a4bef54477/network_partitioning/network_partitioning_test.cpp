#include "network_partitioning.h"
#include "catch.hpp"
#include <vector>
#include <utility>

TEST_CASE("single node") {
    int N = 1;
    std::vector<std::pair<int, int>> edges{};
    std::vector<std::pair<int, int>> compromised{};
    // A single node is inherently connected, so no additional server is required.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 0);
}

TEST_CASE("fully connected without compromised edges") {
    int N = 4;
    std::vector<std::pair<int, int>> edges = { {0, 1}, {1, 2}, {2, 3}, {3, 0} };
    std::vector<std::pair<int, int>> compromised{};
    // The network remains connected; expect 0 additional servers.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 0);
}

TEST_CASE("disconnected due to a compromised edge") {
    int N = 4;
    std::vector<std::pair<int, int>> edges = { {0, 1}, {1, 2}, {2, 3} };
    std::vector<std::pair<int, int>> compromised = { {1, 2} };
    // After removal of edge {1,2}, the network splits into {0,1} and {2,3}.
    // One additional server can connect these two components.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 1);
}

TEST_CASE("multiple isolated nodes (no initial edges)") {
    int N = 5;
    std::vector<std::pair<int, int>> edges{};
    std::vector<std::pair<int, int>> compromised{};
    // Five isolated nodes; one additional server can be connected to all nodes.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 1);
}

TEST_CASE("multiple compromised edges leading to three disconnected components") {
    // Construct a network with 7 nodes divided into three components:
    // Component 1: nodes {0,1,2} with edges (0,1) and (1,2)
    // Component 2: nodes {3,4} with edge (3,4)
    // Component 3: nodes {5,6} with edge (5,6)
    // There are additional connecting edges (2,3) and (4,5) in the original graph.
    // Compromising edges (2,3) and (4,5) disconnects the original network into three components.
    int N = 7;
    std::vector<std::pair<int, int>> edges = { {0, 1}, {1, 2}, {3, 4}, {5, 6}, {2, 3}, {4, 5} };
    std::vector<std::pair<int, int>> compromised = { {2, 3}, {4, 5} };
    // One additional server can be connected to a node from each component.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 1);
}

TEST_CASE("originally disconnected network without compromised edges") {
    // The network has three disjoint components: {0,1}, {2,3}, and {4,5}.
    int N = 6;
    std::vector<std::pair<int, int>> edges = { {0, 1}, {2, 3}, {4, 5} };
    std::vector<std::pair<int, int>> compromised{};
    // One additional server is sufficient to connect all three components.
    REQUIRE(network_partitioning::min_additional_servers(N, edges, compromised) == 1);
}