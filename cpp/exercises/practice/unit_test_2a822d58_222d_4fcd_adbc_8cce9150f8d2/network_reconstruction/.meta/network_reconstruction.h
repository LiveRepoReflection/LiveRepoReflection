#ifndef NETWORK_RECONSTRUCTION_H
#define NETWORK_RECONSTRUCTION_H

#include <vector>
#include <utility>

namespace network_reconstruction {

struct FlowRecord {
    int source;
    int destination;
    int data_amount;
};

std::vector<std::pair<int, int>> reconstruct_network(int N, const std::vector<FlowRecord>& flows, const std::vector<std::vector<int>>& cost);

}  // namespace network_reconstruction

#endif