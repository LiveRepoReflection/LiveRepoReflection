#include "network_optimize.h"
#include <algorithm>
#include <limits>
#include <vector>

namespace network_optimize {

struct Info {
    // total latency and the bottleneck (minimum edge bandwidth along the path)
    // For unreachable paths, latency = INF.
    int latency;
    int bottleneck;
};

const int INF = std::numeric_limits<int>::max();
const int NEG_INF = 0;

int optimal_network_bandwidth(int n, const std::vector<Edge>& edges) {
    // We'll use a modified Floyd–Warshall algorithm.
    // dp[i][j] holds the pair {min total latency from i to j, maximum bottleneck
    // among paths that achieve that minimum latency}
    std::vector<std::vector<Info>> dp(n, std::vector<Info>(n, {INF, NEG_INF}));
    
    // Initialize self paths.
    for (int i = 0; i < n; i++) {
        dp[i][i] = {0, std::numeric_limits<int>::max()};
    }
    
    // For each edge, update dp.
    // Since graph is undirected, update both directions.
    for (const auto& e : edges) {
        int u = e.u, v = e.v;
        Info candidate { e.latency, e.bandwidth };
        // If multiple edges exist between the same nodes, we choose the one with lesser latency.
        // In case of tie in latency, choose the one with greater bottleneck.
        auto updateEdge = [&](int a, int b, const Info &cand) {
            if (cand.latency < dp[a][b].latency) {
                dp[a][b] = cand;
            } else if (cand.latency == dp[a][b].latency) {
                dp[a][b].bottleneck = std::max(dp[a][b].bottleneck, cand.bottleneck);
            }
        };
        updateEdge(u, v, candidate);
        updateEdge(v, u, candidate);
    }
    
    // Floyd–Warshall: for each intermediate node k, try to update i->j using i->k and k->j.
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            if (dp[i][k].latency == INF) continue;
            for (int j = 0; j < n; j++) {
                if (dp[k][j].latency == INF) continue;
                int newLatency = dp[i][k].latency + dp[k][j].latency;
                int newBottleneck = std::min(dp[i][k].bottleneck, dp[k][j].bottleneck);
                if (newLatency < dp[i][j].latency) {
                    dp[i][j] = { newLatency, newBottleneck };
                } else if (newLatency == dp[i][j].latency) {
                    dp[i][j].bottleneck = std::max(dp[i][j].bottleneck, newBottleneck);
                }
            }
        }
    }
    
    // Check connectivity and compute the global minimum bottleneck among all pairs of distinct nodes.
    int answer = std::numeric_limits<int>::max();
    for (int i = 0; i < n; i++) {
        for (int j = i+1; j < n; j++) {
            if (dp[i][j].latency == INF) {
                // Not connected.
                return 0;
            }
            answer = std::min(answer, dp[i][j].bottleneck);
        }
    }
    return answer;
}

}  // namespace network_optimize