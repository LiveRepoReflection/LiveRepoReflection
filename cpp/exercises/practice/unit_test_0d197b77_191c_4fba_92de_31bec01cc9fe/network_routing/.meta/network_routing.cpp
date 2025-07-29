#include "network_routing.h"

void NetworkRouting::initialize(int n) {
    graph.clear();
    node_count = n;
}

void NetworkRouting::add_connection(int node1, int node2, int latency, int bandwidth) {
    graph[node1].push_back({node2, latency, bandwidth});
    graph[node2].push_back({node1, latency, bandwidth});
}

void NetworkRouting::remove_connection(int node1, int node2) {
    auto& edges1 = graph[node1];
    edges1.erase(std::remove_if(edges1.begin(), edges1.end(), 
        [node2](const Edge& e) { return e.to == node2; }), edges1.end());

    auto& edges2 = graph[node2];
    edges2.erase(std::remove_if(edges2.begin(), edges2.end(), 
        [node1](const Edge& e) { return e.to == node1; }), edges2.end());
}

std::vector<int> NetworkRouting::find_best_path(int start_node, int end_node, int min_bandwidth, int max_latency) {
    if (start_node == end_node) return {start_node};

    std::queue<PathInfo> q;
    q.push({start_node, 0, 0, {start_node}});

    std::vector<std::vector<int>> visited(node_count, std::vector<int>(max_latency + 1, INT_MAX));
    visited[start_node][0] = 0;

    std::vector<int> best_path;
    int min_hops = INT_MAX;
    int min_latency = INT_MAX;

    while (!q.empty()) {
        auto current = q.front();
        q.pop();

        if (current.node == end_node) {
            if (current.hops < min_hops || 
                (current.hops == min_hops && current.total_latency < min_latency) ||
                (current.hops == min_hops && current.total_latency == min_latency && current.path < best_path)) {
                min_hops = current.hops;
                min_latency = current.total_latency;
                best_path = current.path;
            }
            continue;
        }

        for (const auto& edge : graph[current.node]) {
            if (edge.bandwidth < min_bandwidth) continue;

            int new_latency = current.total_latency + edge.latency;
            if (new_latency > max_latency) continue;

            if (visited[edge.to][new_latency] > current.hops + 1) {
                visited[edge.to][new_latency] = current.hops + 1;
                PathInfo next = {edge.to, current.hops + 1, new_latency, current.path};
                next.path.push_back(edge.to);
                q.push(next);
            }
        }
    }

    return best_path;
}