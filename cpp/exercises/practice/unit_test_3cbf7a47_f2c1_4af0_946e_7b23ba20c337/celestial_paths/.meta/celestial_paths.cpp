#include "celestial_paths.h"
#include <algorithm>
#include <cmath>
#include <limits>
#include <queue>
#include <random>
#include <unordered_map>
#include <unordered_set>

namespace celestial_paths {

CelestialNetwork::CelestialNetwork(int n, const std::vector<std::tuple<int, int, int, int>>& wormholes) 
    : num_stations_(n) {
    
    // Initialize wormholes_ with the provided wormhole data
    for (const auto& [u, v, min_time, max_time] : wormholes) {
        wormholes_.push_back({u, v, static_cast<double>(min_time), static_cast<double>(max_time)});
    }
}

double CelestialNetwork::calculate_probability(int start_station, int end_station, int allowed_time) {
    // Special case: if start and end are the same, probability is 1.0
    if (start_station == end_station) {
        return 1.0;
    }
    
    // For sufficiently large problems, use Monte Carlo simulation
    const int NUM_SAMPLES = 100000;
    return monte_carlo_shortest_path(start_station, end_station, allowed_time, NUM_SAMPLES);
}

double CelestialNetwork::monte_carlo_shortest_path(int start, int end, int allowed_time, int num_samples) {
    // Use Monte Carlo simulation to estimate the probability
    std::random_device rd;
    std::mt19937 gen(rd());
    
    int successful_samples = 0;
    
    for (int i = 0; i < num_samples; ++i) {
        // Generate random traversal times for each wormhole
        std::vector<double> traversal_times;
        for (const auto& wormhole : wormholes_) {
            std::uniform_real_distribution<double> dist(wormhole.min_time, wormhole.max_time);
            traversal_times.push_back(dist(gen));
        }
        
        // Calculate shortest path with these traversal times
        double shortest_time = shortest_path(start, end, traversal_times);
        
        // Check if it meets the allowed time constraint
        if (shortest_time <= allowed_time) {
            successful_samples++;
        }
    }
    
    return static_cast<double>(successful_samples) / num_samples;
}

double CelestialNetwork::shortest_path(int start, int end, const std::vector<double>& traversal_times) {
    // Build adjacency list for the graph
    std::vector<std::vector<std::pair<int, double>>> adj_list(num_stations_);
    
    for (size_t i = 0; i < wormholes_.size(); ++i) {
        const auto& wormhole = wormholes_[i];
        double time = traversal_times[i];
        
        // Add edges in both directions (undirected graph)
        adj_list[wormhole.u].emplace_back(wormhole.v, time);
        adj_list[wormhole.v].emplace_back(wormhole.u, time);
    }
    
    // Dijkstra's algorithm for shortest path
    std::vector<double> distances(num_stations_, std::numeric_limits<double>::infinity());
    distances[start] = 0.0;
    
    // Priority queue for Dijkstra's algorithm
    std::priority_queue<std::pair<double, int>, 
                        std::vector<std::pair<double, int>>, 
                        std::greater<std::pair<double, int>>> pq;
    pq.emplace(0.0, start);
    
    while (!pq.empty()) {
        auto [dist, node] = pq.top();
        pq.pop();
        
        if (dist > distances[node]) {
            continue;  // Skip if we've already found a better path
        }
        
        for (const auto& [neighbor, weight] : adj_list[node]) {
            if (distances[node] + weight < distances[neighbor]) {
                distances[neighbor] = distances[node] + weight;
                pq.emplace(distances[neighbor], neighbor);
            }
        }
    }
    
    return distances[end];
}

}  // namespace celestial_paths