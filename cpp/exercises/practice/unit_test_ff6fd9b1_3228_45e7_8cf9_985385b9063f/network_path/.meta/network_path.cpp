#include "network_path.h"
#include <queue>
#include <unordered_map>
#include <limits>
#include <algorithm>

struct PathInfo {
    int total_latency;
    int hops;
    std::vector<int> path;
    
    bool operator>(const PathInfo& other) const {
        if (total_latency != other.total_latency)
            return total_latency > other.total_latency;
        return hops > other.hops;
    }
};

struct Edge {
    int dest;
    int latency;
    int bandwidth;
};

std::vector<int> find_optimal_path(
    int n,
    const std::vector<std::tuple<int, int, int, int>>& connections,
    int start_node,
    int end_node,
    int required_bandwidth
) {
    // Validate input parameters
    if (start_node >= n || end_node >= n || start_node < 0 || end_node < 0) {
        return std::vector<int>();
    }

    // Handle special case where start and end are the same
    if (start_node == end_node) {
        return std::vector<int>{start_node};
    }

    // Build adjacency list
    std::vector<std::vector<Edge>> graph(n);
    for (const auto& conn : connections) {
        int node1 = std::get<0>(conn);
        int node2 = std::get<1>(conn);
        int latency = std::get<2>(conn);
        int bandwidth = std::get<3>(conn);

        if (bandwidth >= required_bandwidth) {
            graph[node1].push_back({node2, latency, bandwidth});
            graph[node2].push_back({node1, latency, bandwidth});
        }
    }

    // Priority queue for Dijkstra's algorithm
    std::priority_queue<PathInfo, std::vector<PathInfo>, std::greater<PathInfo>> pq;
    std::vector<bool> visited(n, false);
    
    // Initialize with start node
    pq.push({0, 0, {start_node}});

    while (!pq.empty()) {
        PathInfo current = pq.top();
        pq.pop();
        
        int current_node = current.path.back();
        
        if (visited[current_node]) {
            continue;
        }
        
        visited[current_node] = true;

        // If we reached the destination
        if (current_node == end_node) {
            return current.path;
        }

        // Explore neighbors
        for (const Edge& edge : graph[current_node]) {
            if (!visited[edge.dest]) {
                std::vector<int> new_path = current.path;
                new_path.push_back(edge.dest);
                
                pq.push({
                    current.total_latency + edge.latency,
                    current.hops + 1,
                    new_path
                });
            }
        }
    }

    // No path found
    return std::vector<int>();
}