#ifndef NETWORK_DEPLOY_H
#define NETWORK_DEPLOY_H

#include <vector>
#include <tuple>

namespace network_deploy {

std::vector<int> optimal_network_deploy(int N, int M, const std::vector<std::tuple<int, int, int, int>>& baseStations, int T);

}

#endif