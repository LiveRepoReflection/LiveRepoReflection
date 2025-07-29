#include "quantum_routing.h"
#include <queue>
#include <unordered_map>
#include <cmath>
#include <algorithm>
#include <limits>

namespace quantum_routing {

double find_highest_probability(const std::vector<std::vector<double>>& probabilities,
                              int start, int end) {
    // If start equals end, return 1.0 as the probability of success
    if (start == end) {
        return 1.0;
    }

    int n = probabilities.size();
    
    // We'll use a modified Dijkstra's algorithm to find the path with the highest probability
    // Instead of minimizing distance, we'll maximize probability
    
    // Initialize probabilities array - all nodes start with 0 probability
    std::vector<double> max_probabilities(n, 0.0);
    max_probabilities[start] = 1.0;  // Start node has 100% probability
    
    // Used to keep track of visited nodes
    std::vector<bool> visited(n, false);
    
    // Custom comparator for priority queue - we want to process nodes with higher probabilities first
    // Using negative probabilities because C++ priority queue is a max-heap by default
    auto comparator = [](const std::pair<int, double>& a, const std::pair<int, double>& b) {
        return a.second < b.second;
    };
    
    // Priority queue to hold nodes to visit, ordered by highest probability
    std::priority_queue<std::pair<int, double>, 
                        std::vector<std::pair<int, double>>, 
                        decltype(comparator)> priority_queue(comparator);
    
    // Start with the source node
    priority_queue.push({start, 1.0});
    
    while (!priority_queue.empty()) {
        auto [current_node, prob_to_current] = priority_queue.top();
        priority_queue.pop();
        
        // Skip if we've already processed this node with a better probability
        if (visited[current_node] || prob_to_current < max_probabilities[current_node]) {
            continue;
        }
        
        // Mark current node as visited
        visited[current_node] = true;
        
        // If we've reached the destination, we're done
        if (current_node == end) {
            return max_probabilities[end];
        }
        
        // Check all neighbors of the current node
        for (int next_node = 0; next_node < n; next_node++) {
            // Skip if there's no direct path or if the neighbor has already been visited
            if (probabilities[current_node][next_node] <= 0.0 || visited[next_node]) {
                continue;
            }
            
            // Calculate the probability to reach the neighbor through current node
            double new_probability = max_probabilities[current_node] * probabilities[current_node][next_node];
            
            // If we found a better probability to reach this neighbor, update it
            if (new_probability > max_probabilities[next_node]) {
                max_probabilities[next_node] = new_probability;
                priority_queue.push({next_node, new_probability});
            }
        }
    }
    
    // If we've exhausted all possible paths and haven't reached the end node,
    // then there's no path from start to end
    return max_probabilities[end];
}

}  // namespace quantum_routing