#ifndef QUANTUM_ROUTING_H
#define QUANTUM_ROUTING_H

#include <vector>
#include <tuple>

namespace quantum_routing {
    double find_optimal_path(int N, const std::vector<std::tuple<int, int, double>>& edges, 
                            int S, int D, double swap_penalty);
}

#endif