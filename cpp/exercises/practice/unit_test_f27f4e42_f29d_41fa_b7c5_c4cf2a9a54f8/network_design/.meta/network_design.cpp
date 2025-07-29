#include "network_design.h"
#include <algorithm>
#include <queue>
#include <limits>
#include <unordered_map>
#include <unordered_set>

namespace {
    using Graph = std::vector<std::vector<std::pair<int, int>>>;
    const int INF = std::numeric_limits<int>::max();

    // Ford-Fulkerson implementation with node capacities
    int calculate_flow(const Graph& graph, const std::vector<int>& C, int source, int sink) {
        int n = graph.size();
        std::vector<std::vector<int>> residual(n, std::vector<int>(n, 0));
        
        // Initialize residual graph
        for (int u = 0; u < n; u++) {
            for (const auto& [v, capacity] : graph[u]) {
                residual[u][v] = std::min(capacity, std::min(C[u], C[v]));
            }
        }

        int max_flow = 0;
        while (true) {
            // BFS to find augmenting path
            std::vector<int> parent(n, -1);
            std::queue<int> q;
            q.push(source);
            parent[source] = source;

            while (!q.empty() && parent[sink] == -1) {
                int u = q.front();
                q.pop();

                for (int v = 0; v < n; v++) {
                    if (parent[v] == -1 && residual[u][v] > 0) {
                        parent[v] = u;
                        q.push(v);
                    }
                }
            }

            if (parent[sink] == -1) break;

            // Find minimum residual capacity along the path
            int path_flow = INF;
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                path_flow = std::min(path_flow, residual[u][v]);
            }

            // Update residual capacities
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                residual[u][v] -= path_flow;
                residual[v][u] += path_flow;
            }

            max_flow += path_flow;
        }

        return max_flow;
    }

    // Calculate total network throughput
    int calculate_throughput(const Graph& graph, const std::vector<int>& C) {
        int n = graph.size();
        int total_throughput = 0;

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                total_throughput += calculate_flow(graph, C, i, j);
            }
        }

        return total_throughput;
    }
}

int solve_network_design(int N, int M, const std::vector<int>& C,
                        const std::vector<std::tuple<int, int, int>>& connections,
                        int T) {
    if (M == 0 && T > 0) return -1;

    // Sort connections by cost
    std::vector<std::tuple<int, int, int>> sorted_connections = connections;
    std::sort(sorted_connections.begin(), sorted_connections.end(),
              [](const auto& a, const auto& b) { return std::get<2>(a) < std::get<2>(b); });

    // Try different subsets of connections using binary search
    int left = 1, right = M;
    int min_cost = -1;

    while (left <= right) {
        int mid = left + (right - left) / 2;
        
        // Create graph with first 'mid' cheapest connections
        Graph graph(N);
        int current_cost = 0;

        for (int i = 0; i < mid; i++) {
            const auto& [u, v, w] = sorted_connections[i];
            graph[u].push_back({v, INF});
            graph[v].push_back({u, INF});
            current_cost += w;
        }

        // Check if this configuration meets throughput requirement
        int throughput = calculate_throughput(graph, C);
        
        if (throughput >= T) {
            min_cost = current_cost;
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }

    return min_cost;
}