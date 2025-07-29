#include "network_routing.h"
#include <vector>
#include <tuple>
#include <queue>
#include <limits>
#include <algorithm>

using std::vector;
using std::tuple;
using std::priority_queue;
using std::pair;

namespace network_routing {

int optimize_routing(int N, const vector<tuple<int, int, int>> &connections,
                     const vector<tuple<int, int>> &requests) {
    // Build the undirected graph as an adjacency list
    vector<vector<pair<int, int>>> graph(N);
    for (const auto &edge : connections) {
        int u, v, cost;
        std::tie(u, v, cost) = edge;

        // Check and update for u -> v
        bool found = false;
        for (auto &neighbor : graph[u]) {
            if (neighbor.first == v) {
                neighbor.second = std::min(neighbor.second, cost);
                found = true;
                break;
            }
        }
        if (!found) {
            graph[u].push_back({v, cost});
        }
        
        // Check and update for v -> u (bidirectional)
        found = false;
        for (auto &neighbor : graph[v]) {
            if (neighbor.first == u) {
                neighbor.second = std::min(neighbor.second, cost);
                found = true;
                break;
            }
        }
        if (!found) {
            graph[v].push_back({u, cost});
        }
    }

    int overall_max_latency = 0;

    // Process each request by running Dijkstra's algorithm from source to destination
    for (const auto &req : requests) {
        int src, dst;
        std::tie(src, dst) = req;

        vector<int> dist(N, std::numeric_limits<int>::max());
        dist[src] = 0;

        // Min-heap: pair(distance, node)
        priority_queue<pair<int, int>, vector<pair<int, int>>, std::greater<pair<int, int>>> min_heap;
        min_heap.push({0, src});

        while (!min_heap.empty()) {
            auto current = min_heap.top();
            min_heap.pop();
            int current_dist = current.first;
            int node = current.second;

            if (current_dist > dist[node]) {
                continue;
            }

            // Early exit if destination reached
            if (node == dst) {
                break;
            }
            
            for (const auto &neighbor : graph[node]) {
                int next_node = neighbor.first;
                int edge_cost = neighbor.second;
                if (dist[node] + edge_cost < dist[next_node]) {
                    dist[next_node] = dist[node] + edge_cost;
                    min_heap.push({dist[next_node], next_node});
                }
            }
        }
        overall_max_latency = std::max(overall_max_latency, dist[dst]);
    }
    
    return overall_max_latency;
}

}  // namespace network_routing