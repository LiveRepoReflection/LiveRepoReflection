#include "traffic_flow.h"
#include <queue>
#include <vector>
#include <algorithm>
#include <limits>

namespace traffic_flow {

struct Edge {
    int to;
    int capacity;
    int flow;
    int length;
    int rev;  // Index of reverse edge
};

using Graph = std::vector<std::vector<Edge>>;

// Dijkstra's algorithm to find shortest path
std::vector<int> find_shortest_path(const Graph& g, int s, int t, int n) {
    std::vector<int> dist(n, std::numeric_limits<int>::max());
    std::vector<int> prev(n, -1);
    std::priority_queue<std::pair<int, int>, 
                       std::vector<std::pair<int, int>>,
                       std::greater<>> pq;
    
    dist[s] = 0;
    pq.push({0, s});
    
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        
        if (d > dist[u]) continue;
        
        for (const auto& e : g[u]) {
            if (e.flow < e.capacity) {
                int v = e.to;
                int new_dist = dist[u] + e.length;
                
                if (new_dist < dist[v]) {
                    dist[v] = new_dist;
                    prev[v] = u;
                    pq.push({new_dist, v});
                }
            }
        }
    }
    
    if (dist[t] == std::numeric_limits<int>::max()) {
        return {};
    }
    
    std::vector<int> path;
    for (int v = t; v != -1; v = prev[v]) {
        path.push_back(v);
    }
    std::reverse(path.begin(), path.end());
    return path;
}

// Find minimum residual capacity along a path
int find_min_capacity(const Graph& g, const std::vector<int>& path) {
    int min_cap = std::numeric_limits<int>::max();
    for (size_t i = 0; i < path.size() - 1; ++i) {
        int u = path[i];
        int v = path[i + 1];
        for (const auto& e : g[u]) {
            if (e.to == v) {
                min_cap = std::min(min_cap, e.capacity - e.flow);
                break;
            }
        }
    }
    return min_cap;
}

// Update flow along a path
void update_flow(Graph& g, const std::vector<int>& path, int flow) {
    for (size_t i = 0; i < path.size() - 1; ++i) {
        int u = path[i];
        int v = path[i + 1];
        for (auto& e : g[u]) {
            if (e.to == v) {
                e.flow += flow;
                g[e.to][e.rev].flow -= flow;
                break;
            }
        }
    }
}

bool is_flow_possible(int N, int M, int K,
                     const std::vector<int>& C,
                     const std::vector<int>& U,
                     const std::vector<int>& V,
                     const std::vector<int>& L,
                     const std::vector<int>& R,
                     const std::vector<int>& S,
                     const std::vector<int>& D,
                     const std::vector<int>& T,
                     const std::vector<int>& A) {
    
    // Create residual graph
    Graph g(N);
    
    // Add edges and their reverse edges
    for (int i = 0; i < M; ++i) {
        Edge forward{V[i], R[i], 0, L[i], static_cast<int>(g[V[i]].size())};
        Edge reverse{U[i], 0, 0, -L[i], static_cast<int>(g[U[i]].size())};
        g[U[i]].push_back(forward);
        g[V[i]].push_back(reverse);
    }
    
    // Try to satisfy each commuter's demand
    for (int k = 0; k < K; ++k) {
        int source = S[k];
        int sink = D[k];
        int demand = T[k];
        int max_time = A[k];
        int satisfied_flow = 0;
        
        while (satisfied_flow < demand) {
            // Find shortest path that respects time constraint
            auto path = find_shortest_path(g, source, sink, N);
            if (path.empty()) return false;
            
            // Calculate total time along the path
            int total_time = 0;
            for (size_t i = 0; i < path.size() - 1; ++i) {
                int u = path[i];
                int v = path[i + 1];
                for (const auto& e : g[u]) {
                    if (e.to == v) {
                        total_time += e.length;
                        break;
                    }
                }
            }
            
            if (total_time > max_time) return false;
            
            // Find minimum residual capacity
            int min_cap = find_min_capacity(g, path);
            min_cap = std::min(min_cap, demand - satisfied_flow);
            
            // Check intersection capacity constraints
            for (int node : path) {
                int total_flow = 0;
                for (const auto& e : g[node]) {
                    total_flow += e.flow;
                }
                if (total_flow + min_cap > C[node]) {
                    return false;
                }
            }
            
            // Update flows
            update_flow(g, path, min_cap);
            satisfied_flow += min_cap;
        }
    }
    
    return true;
}

}  // namespace traffic_flow