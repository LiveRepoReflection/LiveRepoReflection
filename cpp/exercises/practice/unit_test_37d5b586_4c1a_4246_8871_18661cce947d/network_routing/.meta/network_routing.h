#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <tuple>

namespace network_routing {

int find_optimal_latency(int N, const std::vector<std::tuple<int, int, int>> &edges, int src, int dest);

}

#endif