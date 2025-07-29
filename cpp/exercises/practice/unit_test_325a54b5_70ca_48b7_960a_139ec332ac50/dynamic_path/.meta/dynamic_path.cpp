#include "dynamic_path.h"
#include <queue>
#include <limits>
#include <algorithm>
#include <unordered_map>

class DynamicPathImpl {
private:
    int n;
    std::vector<std::vector<std::pair<int, long long>>> adj;
    std::unordered_map<long long, int> edgeMap;
    
    long long getEdgeKey(int u, int v) const {
        return (long long)std::min(u, v) * n + std::max(u, v);
    }
    
    long long dijkstra(int start, int end) const {
        std::vector<long long> dist(n, std::numeric_limits<long long>::max());
        std::priority_queue<std::pair<long long, int>, 
                          std::vector<std::pair<long long, int>>, 
                          std::greater<std::pair<long long, int>>> pq;
        
        dist[start] = 0;
        pq.push({0, start});
        
        while (!pq.empty()) {
            auto [d, u] = pq.top();
            pq.pop();
            
            if (d > dist[u]) continue;
            if (u == end) return d;
            
            for (const auto& [v, weight] : adj[u]) {
                if (dist[u] + weight < dist[v]) {
                    dist[v] = dist[u] + weight;
                    pq.push({dist[v], v});
                }
            }
        }
        
        return dist[end];
    }

public:
    DynamicPathImpl(int nodes, const std::vector<std::vector<int>>& edges) : n(nodes) {
        adj.resize(n);
        
        for (const auto& edge : edges) {
            int u = edge[0], v = edge[1];
            long long weight = edge[2];
            
            adj[u].push_back({v, weight});
            adj[v].push_back({u, weight});
            edgeMap[getEdgeKey(u, v)] = weight;
        }
    }
    
    long long findShortestPath(int start, int end) {
        if (start == end) return 0;
        return dijkstra(start, end);
    }
    
    void updateEdge(int u, int v, int newCost) {
        long long key = getEdgeKey(u, v);
        edgeMap[key] = newCost;
        
        // Update both directions in adjacency list
        for (auto& edge : adj[u]) {
            if (edge.first == v) {
                edge.second = newCost;
                break;
            }
        }
        
        for (auto& edge : adj[v]) {
            if (edge.first == u) {
                edge.second = newCost;
                break;
            }
        }
    }
};

DynamicPath::DynamicPath(int n, const std::vector<std::vector<int>>& edges) {
    impl = new DynamicPathImpl(n, edges);
}

long long DynamicPath::findShortestPath(int start, int end) {
    return impl->findShortestPath(start, end);
}

void DynamicPath::updateEdge(int u, int v, int newCost) {
    impl->updateEdge(u, v, newCost);
}

DynamicPath::~DynamicPath() {
    delete impl;
}