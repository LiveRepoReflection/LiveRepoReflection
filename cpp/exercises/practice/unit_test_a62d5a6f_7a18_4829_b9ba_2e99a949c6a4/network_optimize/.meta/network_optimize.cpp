#include "network_optimize.h"
#include <vector>
#include <queue>
#include <unordered_map>
#include <algorithm>
#include <limits>

namespace network_optimize {

class FlowNetwork {
private:
    int V;  // Number of vertices
    std::vector<std::vector<std::unordered_map<int, int>>> adj;  // Adjacency list with edge capacities
    
    bool bfs(int s, int t, std::vector<int>& parent) {
        std::vector<bool> visited(V, false);
        std::queue<int> q;
        
        q.push(s);
        visited[s] = true;
        parent[s] = -1;
        
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            
            for (const auto& edge_map : adj[u]) {
                for (const auto& [v, cap] : edge_map) {
                    if (!visited[v] && cap > 0) {
                        if (v == t) {
                            parent[v] = u;
                            return true;
                        }
                        q.push(v);
                        parent[v] = u;
                        visited[v] = true;
                    }
                }
            }
        }
        return false;
    }
    
    int ford_fulkerson(int s, int t) {
        std::vector<int> parent(V);
        int max_flow = 0;
        
        while (bfs(s, t, parent)) {
            int path_flow = std::numeric_limits<int>::max();
            
            // Find minimum residual capacity along the path
            for (int v = t; v != s; v = parent[v]) {
                int u = parent[v];
                path_flow = std::min(path_flow, adj[u][0][v]);
            }
            
            // Update residual capacities
            for (int v = t; v != s; v = parent[v]) {
                int u = parent[v];
                adj[u][0][v] -= path_flow;
                if (adj[u][0][v] == 0) {
                    adj[u][0].erase(v);
                }
                adj[v][0][u] += path_flow;  // Add reverse edge
            }
            
            max_flow += path_flow;
        }
        
        return max_flow;
    }

public:
    FlowNetwork(int vertices) : V(vertices) {
        adj.resize(V, std::vector<std::unordered_map<int, int>>(1));
    }
    
    void add_edge(int u, int v, int capacity) {
        adj[u][0][v] += capacity;  // Allow multiple edges between same vertices
    }
    
    bool can_satisfy_flow(int source, int sink, int required_flow) {
        // Create a copy of the graph for this flow calculation
        std::vector<std::vector<std::unordered_map<int, int>>> original_adj = adj;
        int max_flow = ford_fulkerson(source, sink);
        adj = original_adj;  // Restore the original graph
        return max_flow >= required_flow;
    }
};

bool can_route_all(int N, 
                  const std::vector<std::tuple<int, int, int>>& edges,
                  const std::vector<std::tuple<int, int, int>>& queries) {
    
    // Handle edge cases first
    for (const auto& [start, end, bandwidth] : queries) {
        // Self-loops or zero bandwidth requests are always satisfied
        if (start == end || bandwidth == 0) {
            continue;
        }
        
        // Create a new flow network for each non-trivial query
        FlowNetwork network(N);
        
        // Add all edges to the network
        for (const auto& [u, v, cap] : edges) {
            network.add_edge(u, v, cap);
            network.add_edge(v, u, cap);  // Add reverse edge for undirected graph
        }
        
        // Check if this query can be satisfied
        if (!network.can_satisfy_flow(start, end, bandwidth)) {
            return false;
        }
    }
    
    // If we made it here, all queries can be satisfied
    return true;
}

} // namespace network_optimize