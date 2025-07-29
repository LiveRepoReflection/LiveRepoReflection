#include "network_routing.h"
#include <queue>
#include <algorithm>

void NetworkRouting::initialize(int N, const std::vector<std::pair<std::pair<int, int>, int>>& edges) {
    num_nodes = N;
    edge_updates.clear();
    adj_list.clear();

    for (const auto& edge : edges) {
        int node1 = edge.first.first;
        int node2 = edge.first.second;
        int cost = edge.second;

        if (node1 > node2) std::swap(node1, node2);

        edge_updates[{node1, node2}].insert({0, cost});
        adj_list[{node1, node2}].push_back({node2, {{0, cost}}});
        adj_list[{node2, node1}].push_back({node1, {{0, cost}}});
    }
}

void NetworkRouting::process_update(int timestamp, int node1, int node2, int new_cost) {
    if (node1 > node2) std::swap(node1, node2);
    edge_updates[{node1, node2}].insert({timestamp, new_cost});
}

int NetworkRouting::get_current_cost(int node1, int node2, int timestamp) const {
    if (node1 > node2) std::swap(node1, node2);
    
    auto it = edge_updates.find({node1, node2});
    if (it == edge_updates.end()) return -1;

    const auto& updates = it->second;
    auto update_it = updates.upper_bound({timestamp, INT_MAX});
    if (update_it == updates.begin()) return -1;

    --update_it;
    return update_it->cost;
}

void NetworkRouting::build_graph_at_timestamp(int timestamp, std::vector<std::vector<int>>& graph) const {
    graph.assign(num_nodes, std::vector<int>(num_nodes, -1));

    for (int i = 0; i < num_nodes; ++i) {
        graph[i][i] = 0;
    }

    for (const auto& edge_list : adj_list) {
        int node1 = edge_list.first.first;
        int node2 = edge_list.first.second;

        int cost = get_current_cost(node1, node2, timestamp);
        if (cost != -1) {
            graph[node1][node2] = cost;
            graph[node2][node1] = cost;
        }
    }
}

int NetworkRouting::query(int query_timestamp, int start_node, int end_node) {
    if (start_node == end_node) return 0;
    if (start_node < 0 || start_node >= num_nodes || end_node < 0 || end_node >= num_nodes) return -1;

    std::vector<std::vector<int>> graph;
    build_graph_at_timestamp(query_timestamp, graph);

    std::vector<int> dist(num_nodes, INT_MAX);
    dist[start_node] = 0;
    std::priority_queue<std::pair<int, int>, std::vector<std::pair<int, int>>, std::greater<>> pq;
    pq.push({0, start_node});

    while (!pq.empty()) {
        auto [current_dist, u] = pq.top();
        pq.pop();

        if (u == end_node) return current_dist;
        if (current_dist > dist[u]) continue;

        for (int v = 0; v < num_nodes; ++v) {
            if (graph[u][v] != -1) {
                int new_dist = current_dist + graph[u][v];
                if (new_dist < dist[v]) {
                    dist[v] = new_dist;
                    pq.push({new_dist, v});
                }
            }
        }
    }

    return -1;
}