#include "quantum_routing.h"
#include <vector>
#include <tuple>
#include <queue>
#include <limits>
#include <cmath>

namespace quantum_routing {

// Define a structure for graph edges.
struct Edge {
    int to;
    double weight;
};

std::vector<double> optimal_routes(
    int N,
    const std::vector<std::tuple<int, int, double>>& edges,
    const std::vector<std::tuple<int, int, double>>& requests,
    double K
) {
    // Build the graph as an adjacency list.
    std::vector<std::vector<Edge>> graph(N);
    for (const auto& edge : edges) {
        int u, v;
        double w;
        std::tie(u, v, w) = edge;
        // Since the graph is undirected, add both directions.
        graph[u].push_back({v, w});
        graph[v].push_back({u, w});
    }

    // Prepare result vector, same order as requests.
    std::vector<double> results(requests.size(), -1);

    // Group requests by source node.
    // Each entry: pair of (request index, destination)
    std::vector<std::vector<std::pair<int, int>>> requests_by_source(N);
    for (size_t i = 0; i < requests.size(); ++i) {
        int s, d;
        double f; // f is not used in our path computation, but is provided
        std::tie(s, d, f) = requests[i];
        requests_by_source[s].push_back({static_cast<int>(i), d});
    }

    // Define Dijkstra's algorithm for each source.
    for (int src = 0; src < N; ++src) {
        if (requests_by_source[src].empty()) {
            continue;
        }

        // Initialize distances.
        std::vector<double> dist(N, std::numeric_limits<double>::infinity());
        dist[src] = 0.0;

        // Priority queue for Dijkstra: (distance, node)
        using PDI = std::pair<double, int>;
        std::priority_queue<PDI, std::vector<PDI>, std::greater<PDI>> pq;
        pq.push({0.0, src});

        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            
            // Skip if we already found a better path
            if (d > dist[u]) continue;
            
            for (const auto& edge : graph[u]) {
                int v = edge.to;
                double w = edge.weight;
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    pq.push({dist[v], v});
                }
            }
        }

        // Process requests from this source.
        for (const auto& req : requests_by_source[src]) {
            int idx = req.first;
            int dest = req.second;
            // If source and destination are the same, distance is 0.
            if (src == dest) {
                results[idx] = 0.0;
            } else if (dist[dest] <= K) {
                // Round the fidelity loss to six decimal places.
                double rounded = std::round(dist[dest] * 1e6) / 1e6;
                results[idx] = rounded;
            } else {
                results[idx] = -1;
            }
        }
    }

    return results;
}

}  // namespace quantum_routing