#if !defined(NETWORK_DEPLOY_H)
#define NETWORK_DEPLOY_H

#include <vector>

namespace network_deploy {

std::vector<int> optimal_placement(
    int num_datacenters,
    const std::vector<int>& capacity,
    const std::vector<std::vector<int>>& network_graph,
    int min_nodes,
    const std::vector<double>& failure_probabilities,
    const std::vector<std::vector<double>>& throughput_matrix
);

} // namespace network_deploy

#endif // NETWORK_DEPLOY_H