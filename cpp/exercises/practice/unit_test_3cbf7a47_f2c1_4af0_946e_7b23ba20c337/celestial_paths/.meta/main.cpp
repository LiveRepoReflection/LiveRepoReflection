#include <iostream>
#include <vector>
#include <tuple>
#include <iomanip>
#include "celestial_paths.h"

int main() {
    int N, M;
    std::cin >> N >> M;
    
    std::vector<std::tuple<int, int, int, int>> wormholes;
    wormholes.reserve(M);
    
    for (int i = 0; i < M; ++i) {
        int u, v, min_time, max_time;
        std::cin >> u >> v >> min_time >> max_time;
        wormholes.emplace_back(u, v, min_time, max_time);
    }
    
    celestial_paths::CelestialNetwork network(N, wormholes);
    
    int Q;
    std::cin >> Q;
    
    for (int i = 0; i < Q; ++i) {
        int start_station, end_station, allowed_time;
        std::cin >> start_station >> end_station >> allowed_time;
        
        double probability = network.calculate_probability(start_station, end_station, allowed_time);
        
        // Output with at least 6 decimal places
        std::cout << std::fixed << std::setprecision(6) << probability << std::endl;
    }
    
    return 0;
}