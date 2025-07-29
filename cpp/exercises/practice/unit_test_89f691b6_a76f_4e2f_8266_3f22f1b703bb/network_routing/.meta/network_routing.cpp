#include "network_routing.h"
#include <queue>
#include <limits>
#include <algorithm>

NetworkRouter::NetworkRouter(int n, const std::vector<Link>& links) : n_(n) {
    // Initialize adjacency list
    adj_list_.resize(n + 1);
    
    // Process all links
    for (const auto& link : links) {
        // Store edge costs in both directions
        edge_costs_[link.u][link.v] = link.cost;
        edge_costs_[link.v][link.u] = link.cost;
        
        // Add edges to adjacency list
        adj_list_[link.u].push_back({link.v, link.cost});
        adj_list_[link.v].push_back({link.u, link.cost});
    }
}

void NetworkRouter::updateNetwork(const std::vector<Update>& updates) {
    for (const auto& update : updates) {
        // Update edge costs
        edge_costs_[update.u][update.v] = update.new_cost;
        edge_costs_[update.v][update.u] = update.new_cost;
        
        // Update adjacency list
        for (auto& edge : adj_list_[update.u]) {
            if (edge.first == update.v) {
                edge.second = update.new_cost;
                break;
            }
        }
        for (auto& edge : adj_list_[update.v]) {
            if (edge.first == update.u) {
                edge.second = update.new_cost;
                break;
            }
        }
    }
}

int NetworkRouter::dijkstra(int source, int dest) {
    std::vector<long long> dist(n_ + 1, std::numeric_limits<long long>::max());
    std::priority_queue<std::pair<long long, int>, 
                       std::vector<std::pair<long long, int>>, 
                       std::greater<>> pq;
    
    dist[source] = 0;
    pq.push({0, source});
    
    while (!pq.empty()) {
        long long d = pq.top().first;
        int u = pq.top().second;
        pq.pop();
        
        if (u == dest) {
            return d;
        }
        
        if (d > dist[u]) {
            continue;
        }
        
        for (const auto& edge : adj_list_[u]) {
            int v = edge.first;
            int cost = edge_costs_[u][v];
            
            if (dist[v] > dist[u] + cost) {
                dist[v] = dist[u] + cost;
                pq.push({dist[v], v});
            }
        }
    }
    
    return -1;  // No path found
}

int NetworkRouter::findOptimalPath(int source, int dest, const std::vector<Update>& updates) {
    // If source and destination are the same
    if (source == dest) {
        return 0;
    }
    
    // Apply updates to the network
    updateNetwork(updates);
    
    // Find shortest path using Dijkstra's algorithm
    return dijkstra(source, dest);
}