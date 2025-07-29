#ifndef INFLUENCE_NETWORK_H
#define INFLUENCE_NETWORK_H

#include <vector>
#include <utility>

namespace influence_network {

int simulateInfluence(int numUsers, const std::vector<std::pair<int, int>> &edges,
                      const std::vector<double> &influenceScores,
                      const std::vector<double> &activationThresholds,
                      const std::vector<int> &initialActivated,
                      int timeSteps);

}

#endif