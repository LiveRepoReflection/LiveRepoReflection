#pragma once

#include <vector>
#include <tuple>

namespace celestial_paths {

class CelestialNetwork {
public:
    // Constructor that initializes the network with the given wormholes
    // n: number of space stations (numbered from 0 to n-1)
    // wormholes: list of (u, v, min_time, max_time) representing wormholes between stations
    CelestialNetwork(int n, const std::vector<std::tuple<int, int, int, int>>& wormholes);
    
    // Calculate probability of reaching end_station from start_station within allowed_time
    double calculate_probability(int start_station, int end_station, int allowed_time);

private:
    struct WormholeInfo {
        int u, v;
        double min_time, max_time;
    };

    int num_stations_;
    std::vector<WormholeInfo> wormholes_;
    
    // Compute shortest path using Monte Carlo sampling
    double monte_carlo_shortest_path(int start, int end, int allowed_time, int num_samples);
    
    // Compute shortest path for a given set of wormhole traversal times
    double shortest_path(int start, int end, const std::vector<double>& traversal_times);
};

}  // namespace celestial_paths