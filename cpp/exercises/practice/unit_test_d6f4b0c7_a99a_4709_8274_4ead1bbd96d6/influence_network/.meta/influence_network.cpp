#include "influence_network.h"
#include <vector>

namespace influence_network {

int simulateInfluence(int numUsers, const std::vector<std::pair<int, int>> &edges,
                      const std::vector<double> &influenceScores,
                      const std::vector<double> &activationThresholds,
                      const std::vector<int> &initialActivated,
                      int timeSteps) {
    if (numUsers <= 0) {
        return 0;
    }
    
    // Build incoming edges list for each node.
    std::vector<std::vector<int>> incomingEdges(numUsers);
    for (const auto &edge : edges) {
        int u = edge.first;
        int v = edge.second;
        if (u >= 0 && u < numUsers && v >= 0 && v < numUsers) {
            incomingEdges[v].push_back(u);
        }
    }
    
    // Initialize activation status for each user.
    std::vector<bool> activated(numUsers, false);
    for (int id : initialActivated) {
        if (id >= 0 && id < numUsers) {
            activated[id] = true;
        }
    }
    
    // Simulation of influence propagation over a fixed number of time steps.
    for (int t = 0; t < timeSteps; ++t) {
        std::vector<int> newActivated;
        for (int v = 0; v < numUsers; ++v) {
            if (!activated[v]) {
                double totalInfluence = 0.0;
                for (int u : incomingEdges[v]) {
                    if (activated[u]) {
                        totalInfluence += influenceScores[u];
                    }
                }
                if (totalInfluence >= activationThresholds[v]) {
                    newActivated.push_back(v);
                }
            }
        }
        if (newActivated.empty()) {
            break;
        }
        for (int v : newActivated) {
            activated[v] = true;
        }
    }
    
    // Count total activated users.
    int count = 0;
    for (bool status : activated) {
        if (status) {
            ++count;
        }
    }
    return count;
}

}