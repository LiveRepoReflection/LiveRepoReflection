#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <tuple>

namespace network_routing {

int optimize_routing(int N, const std::vector<std::tuple<int, int, int>> &connections,
                     const std::vector<std::tuple<int, int>> &requests);

}  // namespace network_routing

#endif