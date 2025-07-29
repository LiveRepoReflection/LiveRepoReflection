#ifndef DELIVERY_NETWORK_H
#define DELIVERY_NETWORK_H

#include <vector>
#include <tuple>

namespace delivery_network {

double computeOptimalCost(int num_cities, const std::vector<std::tuple<int, int, int, int>>& roads, double distance_weight, double toll_weight);

} // namespace delivery_network

#endif // DELIVERY_NETWORK_H