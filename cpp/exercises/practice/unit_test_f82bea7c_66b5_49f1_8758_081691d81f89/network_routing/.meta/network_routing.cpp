#include "network_routing.h"
#include <queue>
#include <set>
#include <limits>
#include <algorithm>
#include <unordered_map>

NetworkRouter::NetworkRouter(int num_nodes) : num_nodes_(num_nodes) {
    adjacency_list_.resize(num_nodes);
}

void NetworkRouter::add_link(int u, int v, int cost) {
    // Remove existing link if present
    remove_link(u, v);
    
    // Add new link to both nodes (undirected graph)
    adjacency_list_[u][v] = cost;
    adjacency_list_[v][u] = cost;
}

void NetworkRouter::remove_link(int u, int v) {
    adjacency_list_[u].erase(v);
    adjacency_list_[v].erase(u);
}

std::vector<int> NetworkRouter::get_optimal_path(int start, int end) {
    if (start == end) {
        return {start};
    }

    // Initialize data structures for Dijkstra's algorithm
    std::vector<int> distances(num_nodes_, std::numeric_limits<int>::max());
    std::vector<int> previous(num_nodes_, -1);
    std::set<std::pair<int, int>> queue; // pair of (distance, node)

    distances[start] = 0;
    queue.insert({0, start});

    while (!queue.empty()) {
        int current = queue.begin()->second;
        queue.erase(queue.begin());

        // Found the destination
        if (current == end) {
            break;
        }

        // Check all neighbors
        for (const auto& neighbor : adjacency_list_[current]) {
            int next = neighbor.first;
            int weight = neighbor.second;
            
            int new_distance = distances[current] + weight;
            
            // If we found a better path
            if (new_distance < distances[next]) {
                // Remove old distance from queue if it exists
                queue.erase({distances[next], next});
                
                // Update distance and previous node
                distances[next] = new_distance;
                previous[next] = current;
                
                // Add new distance to queue
                queue.insert({new_distance, next});
            }
        }
    }

    // If no path was found
    if (previous[end] == -1) {
        return std::vector<int>();
    }

    // Reconstruct path
    std::vector<int> path;
    for (int current = end; current != -1; current = previous[current]) {
        path.push_back(current);
    }
    std::reverse(path.begin(), path.end());

    return path;
}

// Private member variables
class NetworkRouter::Implementation {
public:
    int num_nodes_;
    std::vector<std::unordered_map<int, int>> adjacency_list_;
};