#include "network_routing.h"
#include <queue>
#include <limits>
#include <unordered_map>
#include <string>
#include <vector>
#include <tuple>
#include <algorithm>

namespace network_routing {

    // Structure to represent a unique cable between two cities.
    // For undirected cables, we store the cities in sorted order.
    struct EdgeKey {
        std::string u, v;
        int cost;
        EdgeKey(const std::string &a, const std::string &b, int c) : cost(c) {
            if(a < b) {
                u = a;
                v = b;
            } else {
                u = b;
                v = a;
            }
        }
        bool operator==(const EdgeKey& other) const {
            return u == other.u && v == other.v && cost == other.cost;
        }
    };

    struct EdgeKeyHash {
        std::size_t operator()(const EdgeKey& key) const {
            std::hash<std::string> str_hash;
            std::hash<int> int_hash;
            std::size_t h1 = str_hash(key.u);
            std::size_t h2 = str_hash(key.v);
            std::size_t h3 = int_hash(key.cost);
            return ((h1 ^ (h2 << 1)) >> 1) ^ (h3 << 1);
        }
    };

    // Dijkstra's algorithm to obtain the shortest path in terms of cable cost from src to dst.
    // Returns a vector of EdgeKey representing the path. If no valid path exists, returns an empty vector.
    std::vector<EdgeKey> dijkstra_path(const Graph& graph, const std::string& src, const std::string& dst) {
        using NodeDist = std::pair<int, std::string>;
        std::unordered_map<std::string, int> dist;
        std::unordered_map<std::string, std::pair<std::string, int>> prev;
        
        for (const auto& kv : graph) {
            dist[kv.first] = std::numeric_limits<int>::max();
        }
        dist[src] = 0;
        
        std::priority_queue<NodeDist, std::vector<NodeDist>, std::greater<NodeDist>> pq;
        pq.push({0, src});
        
        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            if (d > dist[u])
                continue;
            if (u == dst)
                break;
            // Iterate through all adjacent cables.
            for (const auto& neighbor : graph.at(u)) {
                const std::string& v = neighbor.first;
                int w = neighbor.second;
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w;
                    prev[v] = {u, w};
                    pq.push({dist[v], v});
                }
            }
        }
        
        if (dist[dst] == std::numeric_limits<int>::max()) {
            return {};
        }
        
        // Reconstruct the path from dst to src.
        std::vector<EdgeKey> path;
        std::string current = dst;
        while (current != src) {
            auto it = prev.find(current);
            if (it == prev.end()) {
                return {};
            }
            std::string parent = it->second.first;
            int edge_cost = it->second.second;
            path.push_back(EdgeKey(parent, current, edge_cost));
            current = parent;
        }
        std::reverse(path.begin(), path.end());
        return path;
    }

    double optimize_network_routing(const Graph& graph, const std::vector<Transfer>& transfers) {
        // Map to hold aggregated load on each cable (EdgeKey).
        std::unordered_map<EdgeKey, int, EdgeKeyHash> edge_load;
        long long total_cost = 0;

        // Process each data transfer by computing its shortest path.
        for (const auto& transfer : transfers) {
            std::string src, dst;
            int data;
            std::tie(src, dst, data) = transfer;
            std::vector<EdgeKey> path = dijkstra_path(graph, src, dst);
            if (path.empty()) {
                return std::numeric_limits<double>::infinity();
            }
            // For each cable used in the transfer, add the data load and cost contribution.
            for (const auto& edge : path) {
                edge_load[edge] += data;
                total_cost += static_cast<long long>(edge.cost) * data;
            }
        }

        int max_load = 0;
        for (const auto& kv : edge_load) {
            if (kv.second > max_load) {
                max_load = kv.second;
            }
        }

        double result = max_load + total_cost;
        return result;
    }

} // namespace network_routing