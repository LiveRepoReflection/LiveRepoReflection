#ifndef QUANTUM_ROUTING_H
#define QUANTUM_ROUTING_H

#include <vector>
#include <tuple>

namespace quantum_routing {

std::vector<double> optimal_routes(
    int N,
    const std::vector<std::tuple<int, int, double>>& edges,
    const std::vector<std::tuple<int, int, double>>& requests,
    double K
);

}

#endif  // QUANTUM_ROUTING_H