#include "quantum_routing.h"
#include <algorithm>
#include <queue>
#include <vector>
#include <unordered_map>
#include <cmath>
#include <limits>

namespace quantum_routing {

double find_optimal_path(int N, const std::vector<std::tuple<int, int, double>>& edges, 
                        int S, int D, double swap_penalty) {
    // Create adjacency list with highest fidelity for each edge
    std::vector<std::unordered_map<int, double>> graph(N);
    
    for (const auto& edge : edges) {
        int u = std::get<0>(edge);
        int v = std::get<1>(edge);
        double fidelity = std::get<2>(edge);
        
        // Since we're finding max probability, we need to keep the edge with max fidelity
        // when there are multiple edges between the same nodes
        if (graph[u].find(v) == graph[u].end() || graph[u][v] < fidelity) {
            graph[u][v] = fidelity;
        }
        
        // Undirected graph
        if (graph[v].find(u) == graph[v].end() || graph[v][u] < fidelity) {
            graph[v][u] = fidelity;
        }
    }
    
    // Modified Dijkstra's algorithm to find path with maximum probability
    // We'll use negative log probabilities to turn multiplication into addition
    // and find the shortest path (highest probability)
    
    // Initialize distances (using negative log probability)
    std::vector<double> distance(N, std::numeric_limits<double>::infinity());
    distance[S] = 0.0;
    
    // Track entanglement swaps needed for each path
    std::vector<int> swaps(N, 0);
    
    // Priority queue for Dijkstra's algorithm
    // We use pair<double, int> for <negative log probability, node>
    std::priority_queue<std::pair<double, int>, 
                        std::vector<std::pair<double, int>>, 
                        std::greater<std::pair<double, int>>> pq;
    
    pq.push({0.0, S});
    
    while (!pq.empty()) {
        double current_neg_log_prob = pq.top().first;
        int current_node = pq.top().second;
        pq.pop();
        
        // If we've already found a better path to this node, skip
        if (current_neg_log_prob > distance[current_node]) {
            continue;
        }
        
        // Process all neighbors
        for (const auto& neighbor_entry : graph[current_node]) {
            int neighbor = neighbor_entry.first;
            double edge_fidelity = neighbor_entry.second;
            
            // Calculate new negative log probability
            // For the edge: -log(edge_fidelity)
            // For each entanglement swap: -log(swap_penalty)
            double new_swaps = (current_node == S) ? 0 : swaps[current_node] + 1;
            double new_neg_log_prob = current_neg_log_prob - log(edge_fidelity);
            
            // Add penalty for entanglement swaps except for the destination node
            // Since the swap happens at the next node, not at the current node
            if (neighbor != D) {
                new_neg_log_prob -= log(swap_penalty);
            }
            
            // Update if this path has higher probability (lower negative log probability)
            if (new_neg_log_prob < distance[neighbor]) {
                distance[neighbor] = new_neg_log_prob;
                swaps[neighbor] = new_swaps;
                pq.push({new_neg_log_prob, neighbor});
            }
        }
    }
    
    // Check if a path was found
    if (std::isinf(distance[D])) {
        return 0.0;  // No path exists
    }
    
    // Convert back from negative log probability to actual probability
    return exp(-distance[D]);
}

}  // namespace quantum_routing