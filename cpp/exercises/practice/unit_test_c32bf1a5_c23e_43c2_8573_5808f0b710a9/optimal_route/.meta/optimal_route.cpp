#include "optimal_route.h"
#include <vector>
#include <tuple>
#include <algorithm>
#include <limits>
#include <unordered_map>
#include <queue>

namespace optimal_route {

// Utility function to compute shortest paths between all pairs of intersections
std::vector<std::vector<int>> compute_all_shortest_paths(
    int num_intersections,
    const std::vector<std::tuple<int, int, int>>& edges
) {
    // Initialize distance matrix with infinity
    std::vector<std::vector<int>> dist(
        num_intersections, 
        std::vector<int>(num_intersections, std::numeric_limits<int>::max())
    );
    
    // Set diagonal elements to 0
    for (int i = 0; i < num_intersections; ++i) {
        dist[i][i] = 0;
    }
    
    // Set direct edge weights
    for (const auto& edge : edges) {
        int start = std::get<0>(edge);
        int end = std::get<1>(edge);
        int weight = std::get<2>(edge);
        dist[start][end] = weight;
    }
    
    // Floyd-Warshall algorithm to find shortest paths
    for (int k = 0; k < num_intersections; ++k) {
        for (int i = 0; i < num_intersections; ++i) {
            for (int j = 0; j < num_intersections; ++j) {
                if (dist[i][k] != std::numeric_limits<int>::max() && 
                    dist[k][j] != std::numeric_limits<int>::max() &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
    
    return dist;
}

// Helper function for memoized recursion to find minimum travel time
int solve_tsp_recursive(
    int current,
    unsigned int visited_mask,
    int num_customers,
    int depot_intersection,
    const std::vector<int>& customer_indices,
    const std::vector<std::vector<int>>& shortest_paths,
    std::vector<std::vector<int>>& memo
) {
    // If all customers have been visited, return to depot
    if (visited_mask == (1U << num_customers) - 1) {
        return shortest_paths[current][depot_intersection];
    }
    
    // If we've already computed this state, return memoized result
    if (memo[current][visited_mask] != -1) {
        return memo[current][visited_mask];
    }
    
    int min_time = std::numeric_limits<int>::max();
    
    // Try visiting each unvisited customer next
    for (int i = 0; i < num_customers; ++i) {
        if (!(visited_mask & (1U << i))) {  // if customer i has not been visited
            int next_customer = customer_indices[i];
            int new_time = shortest_paths[current][next_customer] + 
                           solve_tsp_recursive(
                               next_customer, 
                               visited_mask | (1U << i), 
                               num_customers, 
                               depot_intersection, 
                               customer_indices, 
                               shortest_paths, 
                               memo
                           );
            min_time = std::min(min_time, new_time);
        }
    }
    
    // Memoize and return result
    memo[current][visited_mask] = min_time;
    return min_time;
}

int min_travel_time(
    int num_intersections,
    const std::vector<std::tuple<int, int, int>>& edges,
    int depot_intersection,
    const std::vector<int>& customer_intersections,
    int max_route_time
) {
    // Precompute shortest paths between all pairs of intersections
    std::vector<std::vector<int>> shortest_paths = compute_all_shortest_paths(num_intersections, edges);
    
    int num_customers = customer_intersections.size();
    
    // Initialize memo table for dynamic programming
    // Key is (current_node, visited_mask)
    // Value is the minimum travel time from current node to depot while visiting all unvisited customers
    std::vector<std::vector<int>> memo(
        num_intersections, 
        std::vector<int>(1 << num_customers, -1)
    );
    
    // Start from depot with no customers visited
    int optimal_time = solve_tsp_recursive(
        depot_intersection, 
        0, 
        num_customers, 
        depot_intersection, 
        customer_intersections, 
        shortest_paths, 
        memo
    );
    
    // Check if the optimal route satisfies the time constraint
    return (optimal_time <= max_route_time) ? optimal_time : -1;
}

}  // namespace optimal_route