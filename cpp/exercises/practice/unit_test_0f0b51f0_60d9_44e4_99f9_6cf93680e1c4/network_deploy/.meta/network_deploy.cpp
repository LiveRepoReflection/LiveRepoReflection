#include "network_deploy.h"
#include <vector>
#include <limits>
#include <queue>

namespace network_deploy {

// Helper function to compute MST cost using Prim's algorithm on the graph defined by matrix C.
int compute_mst_cost(int N, const std::vector<std::vector<int>>& C) {
    // Use a simple O(N^2) Prim's algorithm since N <= 200.
    std::vector<bool> inMST(N, false);
    std::vector<int> key(N, std::numeric_limits<int>::max());
    key[0] = 0;
    int totalCost = 0;

    for (int i = 0; i < N; ++i) {
        int u = -1;
        int best = std::numeric_limits<int>::max();
        for (int v = 0; v < N; ++v) {
            if (!inMST[v] && key[v] < best) {
                best = key[v];
                u = v;
            }
        }
        if (u == -1) break;
        inMST[u] = true;
        totalCost += key[u];
        for (int v = 0; v < N; ++v) {
            // Avoid self-loop and only update if not in MST and we found a cheaper edge.
            if (!inMST[v] && C[u][v] < key[v]) {
                key[v] = C[u][v];
            }
        }
    }
    return totalCost;
}

int optimal_network_deployment(int N, int R, const std::vector<std::vector<int>>& B, const std::vector<std::vector<int>>& C, int RelayCost) {
    // If no relay stations can be deployed (R == 0), we must use direct links.
    if(R == 0) {
        // Compute MST cost on the direct link graph.
        return compute_mst_cost(N, C);
    }
    
    // If relay stations are available, we decide to use a relay‐based connectivity.
    // In this model, if at least one relay is deployed then all nodes must “hook‐up”
    // to a relay network. However, the quality (i.e. effective capacity) of the relay
    // network depends on how many relay stations are used. The cost for a node to adopt
    // relay connectivity using r relay stations is: r * RelayCost.
    // For every pair of nodes the effective relay “link” cost will be the sum for both nodes.
    // In order for the network to be acceptable for all pairs, one might require a minimum
    // effective relay cost. For our purposes we mimic the following decision process:
    //
    //   Let req = max{ B[i][j] : 0 <= i, j < N, i != j }.
    //   If it is possible to meet req with less than or equal to R relay stations,
    //   then one may choose r = ceil(req / RelayCost). Otherwise, the best available is r = R.
    //
    // The total cost for using the relay network is then: N * (r * RelayCost).
    //
    // Note: This design forces a homogeneous deployment if relay stations are used.
    
    int req = 0;
    for (int i = 0; i < N; ++i) {
        for(int j = 0; j < N; ++j) {
            if(i != j && B[i][j] > req) {
                req = B[i][j];
            }
        }
    }
    // Compute the minimum number of relay stations required to meet the maximum bandwidth req.
    int rNeeded = (req + RelayCost - 1) / RelayCost;  // Ceiling division.
    int r = (rNeeded <= R ? rNeeded : R);
    
    // Total relay based cost: every node must connect to r relay stations.
    int relayTotalCost = N * (r * RelayCost);
    
    // In this problem formulation, when relay stations are available, the network
    // must be deployed uniformly – i.e. one cannot mix direct links and relay connections.
    // Hence, we choose the relay option.
    return relayTotalCost;
}

}  // namespace network_deploy