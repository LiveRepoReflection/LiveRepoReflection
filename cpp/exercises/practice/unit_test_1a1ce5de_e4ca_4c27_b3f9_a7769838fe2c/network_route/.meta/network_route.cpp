#include "network_route.h"
#include <queue>
#include <limits>
#include <unordered_map>
#include <map>
#include <algorithm>
#include <vector>
#include <set>

// Structure to represent nodes in priority queue
struct Node {
    int id;
    double avg_latency;
    int total_latency;
    int hops;
    std::vector<int> path;

    // Custom comparison operator for priority queue
    bool operator>(const Node& other) const {
        // Primary: compare by average latency
        if (avg_latency != other.avg_latency) {
            return avg_latency > other.avg_latency;
        }
        // Secondary: if average latency is equal, prefer shorter paths
        return hops > other.hops;
    }
};

std::vector<int> find_optimal_route(int N, 
                                   const std::vector<std::tuple<int, int, int>>& links,
                                   int S, 
                                   int D) {
    // Handle edge case: source and destination are the same
    if (S == D) {
        return {S};
    }

    // Build adjacency list representation of the graph
    std::vector<std::map<int, std::set<int>>> graph(N);
    
    for (const auto& link : links) {
        int u = std::get<0>(link);
        int v = std::get<1>(link);
        int latency = std::get<2>(link);

        // Add both directions (bidirectional links)
        graph[u][v].insert(latency);
        graph[v][u].insert(latency);
    }

    // Initialize priority queue for Dijkstra's algorithm modified for average latency
    std::priority_queue<Node, std::vector<Node>, std::greater<Node>> pq;
    
    // Start from source with 0 latency and a path containing only the source
    std::vector<int> initial_path = {S};
    pq.push({S, 0.0, 0, 0, initial_path});
    
    // Keep track of visited nodes with their best average latency
    std::unordered_map<int, double> best_avg_latency;
    
    // Modified Dijkstra's algorithm to find path with minimum average latency
    while (!pq.empty()) {
        Node current = pq.top();
        pq.pop();
        
        int node_id = current.id;
        double current_avg = current.avg_latency;
        int current_total = current.total_latency;
        int current_hops = current.hops;
        std::vector<int> current_path = current.path;
        
        // If we've reached the destination, return the path
        if (node_id == D) {
            return current_path;
        }
        
        // Skip if we've found a better average latency path to this node already
        if (best_avg_latency.find(node_id) != best_avg_latency.end() && 
            best_avg_latency[node_id] < current_avg) {
            continue;
        }
        
        // Update best average latency for this node
        best_avg_latency[node_id] = current_avg;
        
        // Explore neighbors
        for (const auto& neighbor_entry : graph[node_id]) {
            int neighbor = neighbor_entry.first;
            
            // Skip if we're going back to a node already in our path
            if (std::find(current_path.begin(), current_path.end(), neighbor) != current_path.end()) {
                continue;
            }
            
            // Consider all possible latencies for this edge
            for (int latency : neighbor_entry.second) {
                int new_total = current_total + latency;
                int new_hops = current_hops + 1;
                double new_avg = new_total / static_cast<double>(new_hops);
                
                // Create a new path including this neighbor
                std::vector<int> new_path = current_path;
                new_path.push_back(neighbor);
                
                // Push to priority queue
                pq.push({neighbor, new_avg, new_total, new_hops, new_path});
            }
        }
    }
    
    // If we reach here, no path was found
    return {};
}