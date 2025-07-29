#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <string>
#include <vector>
#include <unordered_map>
#include <tuple>

namespace network_routing {

    using Graph = std::unordered_map<std::string, std::vector<std::pair<std::string, int>>>;
    using Transfer = std::tuple<std::string, std::string, int>;

    double optimize_network_routing(const Graph& graph, const std::vector<Transfer>& transfers);

} // namespace network_routing

#endif