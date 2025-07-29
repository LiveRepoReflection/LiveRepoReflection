#include "route_optimizer.h"
#include <vector>
#include <queue>
#include <tuple>
#include <unordered_map>
#include <limits>
#include <algorithm>

struct State {
    int node;
    int time;
    int toll;
    int congestion;
    
    // Comparison operator for priority queue (min heap)
    bool operator>(const State& other) const {
        return congestion > other.congestion;
    }
};

int solve(int n, const std::vector<std::tuple<int, int, int, int, int>>& edges, 
          int start, int destination, int max_travel_time, int max_toll_cost) {
    
    // If start and destination are the same, return 0
    if (start == destination) {
        return 0;
    }
    
    // Build adjacency list for the graph
    std::vector<std::vector<std::tuple<int, int, int, int>>> graph(n);
    for (const auto& edge : edges) {
        int from = std::get<0>(edge);
        int to = std::get<1>(edge);
        int time = std::get<2>(edge);
        int toll = std::get<3>(edge);
        int congestion = std::get<4>(edge);
        
        graph[from].push_back(std::make_tuple(to, time, toll, congestion));
    }
    
    // Initialize a 3D dp table to keep track of minimum congestion
    // dp[node][time][toll] = minimum congestion to reach node with time and toll
    // Using a map to save space, as most states may not be reachable
    std::vector<std::vector<std::unordered_map<int, int>>> dp(
        n, std::vector<std::unordered_map<int, int>>(max_travel_time + 1)
    );
    
    // Initialize all states to infinity
    for (int i = 0; i < n; i++) {
        for (int t = 0; t <= max_travel_time; t++) {
            dp[i][t][0] = std::numeric_limits<int>::max();
        }
    }
    
    // Priority queue to process states with lowest congestion first
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;
    
    // Start with 0 congestion at start node
    pq.push({start, 0, 0, 0});
    dp[start][0][0] = 0;
    
    // Set to keep track of visited states for optimization
    std::vector<std::vector<std::unordered_map<int, bool>>> visited(
        n, std::vector<std::unordered_map<int, bool>>(max_travel_time + 1)
    );
    
    while (!pq.empty()) {
        auto [node, time, toll, congestion] = pq.top();
        pq.pop();
        
        // If we've reached the destination, return the congestion
        if (node == destination) {
            return congestion;
        }
        
        // Skip if we've already processed this state or found a better path
        if (visited[node][time][toll]) {
            continue;
        }
        
        visited[node][time][toll] = true;
        
        // Try all outgoing edges
        for (const auto& [next, edge_time, edge_toll, edge_congestion] : graph[node]) {
            int new_time = time + edge_time;
            int new_toll = toll + edge_toll;
            int new_congestion = congestion + edge_congestion;
            
            // Check if we exceed constraints
            if (new_time > max_travel_time || new_toll > max_toll_cost) {
                continue;
            }
            
            // Check if this is a better path to next node with given time and toll
            auto& next_dp = dp[next][new_time];
            if (next_dp.find(new_toll) == next_dp.end() || new_congestion < next_dp[new_toll]) {
                next_dp[new_toll] = new_congestion;
                pq.push({next, new_time, new_toll, new_congestion});
            }
        }
    }
    
    // If we couldn't reach the destination within constraints
    return -1;
}