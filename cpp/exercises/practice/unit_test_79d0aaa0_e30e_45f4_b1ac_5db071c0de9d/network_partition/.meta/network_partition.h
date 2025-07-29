#ifndef NETWORK_PARTITION_H
#define NETWORK_PARTITION_H

#include <vector>
#include <tuple>

std::vector<int> partitionNetwork(int n, const std::vector<std::tuple<int, int, int>>& edges, const std::vector<int>& costs, double lambda);

#endif