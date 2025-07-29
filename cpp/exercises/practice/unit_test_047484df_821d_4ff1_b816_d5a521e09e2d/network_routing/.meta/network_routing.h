#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <tuple>

namespace network_routing {

    // Process routing requests over the network.
    // Parameters:
    //  N: number of nodes (0-indexed, total nodes = N)
    //  links: vector of tuples (u, v, capacity, base_latency)
    //  requests: vector of tuples (src, dest, data)
    // Returns:
    //  vector of double where each value corresponds to the total latency for that request,
    //  or -1 if the request cannot be routed.
    std::vector<double> processRequests(
        int N,
        const std::vector<std::tuple<int, int, int, int>>& links,
        const std::vector<std::tuple<int, int, int>>& requests
    );

} // namespace network_routing

#endif