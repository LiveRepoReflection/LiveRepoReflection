#ifndef NETWORK_DEPLOY_H
#define NETWORK_DEPLOY_H

#include <vector>

namespace network_deploy {

int optimal_network_deployment(int N, int R, const std::vector<std::vector<int>>& B, const std::vector<std::vector<int>>& C, int RelayCost);

}  // namespace network_deploy

#endif  // NETWORK_DEPLOY_H