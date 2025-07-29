#include <vector>
#include <queue>
#include <utility>
#include <cstdlib>
#include <algorithm>
#include "catch.hpp"
#include "network_reconstruction.h"

using namespace std;
using namespace network_reconstruction;

// Helper function to perform a BFS on the reconstructed graph and check connectivity.
bool is_connected(int N, const vector<pair<int, int>> &edges, int src, int dst) {
    if (src == dst) return true;
    vector<vector<int>> adj(N);
    for (const auto &edge : edges) {
        int u = edge.first, v = edge.second;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    vector<bool> visited(N, false);
    queue<int> q;
    q.push(src);
    visited[src] = true;
    while (!q.empty()) {
        int cur = q.front();
        q.pop();
        if (cur == dst) return true;
        for (int nbr : adj[cur])
            if (!visited[nbr]) {
                visited[nbr] = true;
                q.push(nbr);
            }
    }
    return false;
}

// Helper function to compute total cost of the network given a cost matrix.
int total_network_cost(const vector<pair<int, int>> &edges, const vector<vector<int>> &cost) {
    int sum = 0;
    for (const auto &edge : edges) {
        int u = edge.first, v = edge.second;
        sum += cost[u][v];
    }
    return sum;
}

// Test when there are no flow records.
// The expected network is empty when there is no requirement to connect nodes.
TEST_CASE("empty_flow_records") {
    int N = 5;
    vector<FlowRecord> flows;
    // Create a cost matrix where cost(u, v) = abs(u-v)+1
    vector<vector<int>> cost(N, vector<int>(N, 0));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : abs(i - j) + 1;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    REQUIRE(edges.empty());
}

// Test when flow is self-referential. No edge should be necessary.
TEST_CASE("self_flow") {
    int N = 3;
    vector<FlowRecord> flows = {
        {0, 0, 10},
        {1, 1, 5}
    };
    vector<vector<int>> cost(N, vector<int>(N, 0));
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : abs(i - j) + 1;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    // Since flows are self-referential, no connections are required.
    REQUIRE(edges.empty());
}

// Test with a simple two-node flow.
TEST_CASE("simple_two_node_flow") {
    int N = 2;
    vector<FlowRecord> flows = {
        {0, 1, 5}
    };
    vector<vector<int>> cost(N, vector<int>(N, 0));
    // Cost function: cost(u,v) = (abs(u-v) + 1)*2
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : (abs(i - j) + 1) * 2;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    // There must be a connection between node 0 and 1.
    REQUIRE(is_connected(N, edges, 0, 1));
}

// Test using sample flows from the problem description.
TEST_CASE("sample_network") {
    // N=4, flows: (0,2,10), (1,3,5), (0,3,7)
    int N = 4;
    vector<FlowRecord> flows = {
        {0, 2, 10},
        {1, 3, 5},
        {0, 3, 7}
    };
    
    // Define cost function as cost(u,v) = abs(u-v)*2.
    vector<vector<int>> cost(N, vector<int>(N, 0));
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            cost[i][j] = (i == j) ? 0 : abs(i - j) * 2;
    
    auto edges = reconstruct_network(N, flows, cost);
    
    // Check connectivity for every flow.
    for (const auto &flow : flows) {
        // If source equals destination, skip the connectivity test.
        if (flow.source == flow.destination) continue;
        bool conn = is_connected(N, edges, flow.source, flow.destination);
        INFO("Flow from " << flow.source << " to " << flow.destination << " not connected.");
        REQUIRE(conn);
    }
    
    // Although multiple correct results might exist, check that the total cost 
    // does not exceed an expected threshold computed from the sample optimal solution.
    // For example, one candidate optimal solution is: edges {(0,1), (1,2), (1,3)}
    // with total cost 2 + 2 + 4 = 8.
    int totalCost = total_network_cost(edges, cost);
    INFO("Total network cost: " << totalCost);
    REQUIRE(totalCost <= 8);
}

// Test with duplicate flows between same nodes.
TEST_CASE("duplicate_flows") {
    int N = 4;
    vector<FlowRecord> flows = {
        {0, 1, 5},
        {0, 1, 3},
        {1, 2, 4},
        {2, 3, 7},
        {0, 3, 6}
    };
    
    vector<vector<int>> cost(N, vector<int>(N, 0));
    // Define a simple cost function: cost(u,v) = (abs(u-v) + 1)*3
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : (abs(i - j) + 1) * 3;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    
    // Validate connectivity for each flow.
    for (const auto &flow : flows) {
        if (flow.source == flow.destination) continue;
        REQUIRE(is_connected(N, edges, flow.source, flow.destination));
    }
}

// Test a scenario with disconnected sub-networks. Only flows within sub-networks are provided.
TEST_CASE("disconnected_subnetworks") {
    int N = 6;
    vector<FlowRecord> flows = {
        {0, 1, 12},
        {1, 2, 8},
        {3, 4, 10},
        {4, 5, 15}
    };
    
    vector<vector<int>> cost(N, vector<int>(N, 0));
    // Define cost function: cost(u,v) = (abs(u-v) + 2)
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : abs(i - j) + 2;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    
    // Check connectivity within first subnetwork (nodes 0,1,2)
    REQUIRE(is_connected(N, edges, 0, 2));
    // Check connectivity within second subnetwork (nodes 3,4,5)
    REQUIRE(is_connected(N, edges, 3, 5));
    
    // There is no flow between subnetworks.
    // It is acceptable that there's no path between any node from the first subnetwork and any node from the second.
    bool anyConnection = false;
    for (int u : {0,1,2}) {
        for (int v : {3,4,5}) {
            if (is_connected(N, edges, u, v)) {
                anyConnection = true;
                break;
            }
        }
        if (anyConnection) break;
    }
    REQUIRE_FALSE(anyConnection);
}

// Test to ensure that multiple valid reconstructions still meet flow connectivity requirements.
TEST_CASE("multiple_valid_reconstructions") {
    int N = 5;
    vector<FlowRecord> flows = {
        {0, 2, 9},
        {2, 4, 5},
        {0, 4, 7},
        {1, 3, 4}
    };
    
    vector<vector<int>> cost(N, vector<int>(N, 0));
    // Define cost function: cost(u,v) = (abs(u-v) * 2 + 1)
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            cost[i][j] = (i == j) ? 0 : abs(i - j) * 2 + 1;
        }
    }
    
    auto edges = reconstruct_network(N, flows, cost);
    
    // Validate connectivity for each flow.
    for (const auto &flow : flows) {
        if (flow.source == flow.destination) continue;
        REQUIRE(is_connected(N, edges, flow.source, flow.destination));
    }
}