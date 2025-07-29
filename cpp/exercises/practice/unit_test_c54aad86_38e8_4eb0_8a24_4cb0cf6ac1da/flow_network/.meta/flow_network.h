#ifndef FLOW_NETWORK_H_
#define FLOW_NETWORK_H_

#include <vector>
#include <tuple>

namespace flow_network {

std::vector<std::tuple<int, int, double>> design_network(
    int N,
    const std::vector<std::tuple<int, int, double>>& edges,
    const std::vector<std::tuple<int, int, double>>& commodities);

}  // namespace flow_network

#endif  // FLOW_NETWORK_H_