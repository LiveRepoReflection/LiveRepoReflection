#ifndef NETWORK_OPTIMIZE_H
#define NETWORK_OPTIMIZE_H

#include <vector>

namespace network_optimize {

struct Edge {
    int u;
    int v;
    int latency;
    int bandwidth;
};

int optimal_network_bandwidth(int n, const std::vector<Edge>& edges);

}  // namespace network_optimize

#endif  // NETWORK_OPTIMIZE_H