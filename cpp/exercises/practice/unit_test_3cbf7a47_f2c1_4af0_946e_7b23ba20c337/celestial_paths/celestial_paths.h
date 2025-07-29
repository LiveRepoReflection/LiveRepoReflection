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
    // Add any private methods and member variables needed by your implementation
};

}  // namespace celestial_paths