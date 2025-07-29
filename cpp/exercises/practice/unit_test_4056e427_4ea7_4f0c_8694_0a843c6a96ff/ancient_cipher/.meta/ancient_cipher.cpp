#include "ancient_cipher.h"
#include <vector>
#include <tuple>
#include <utility>
#include <limits>
#include <algorithm>

namespace ancient_cipher {

std::pair<std::vector<int>, int> solve(int N, const std::vector<int>& V, const std::vector<std::tuple<int, int, int>>& roads, int start_city, int end_city, int K) {
    const int INF_NEG = std::numeric_limits<int>::min();
    // dp[k][v] holds the maximum net value achievable from start_city to v using exactly k edges.
    std::vector<std::vector<int>> dp(K + 1, std::vector<int>(N, INF_NEG));
    // parent[k][v] stores the previous node and the edge count index (k-1) used to reach node v at step k.
    std::vector<std::vector<std::pair<int, int>>> parent(K + 1, std::vector<std::pair<int, int>>(N, {-1, -1}));

    // Base initialization: 0 edges from start_city gives a net value equal to the value of start_city.
    dp[0][start_city] = V[start_city];

    // Dynamic programming: relax edges for each allowed number of edges up to K.
    for (int k = 0; k < K; ++k) {
        for (int u = 0; u < N; ++u) {
            if (dp[k][u] == INF_NEG) continue;
            // Explore all roads starting from u.
            for (const auto& edge : roads) {
                int from, to, cost;
                std::tie(from, to, cost) = edge;
                if (from != u) continue;
                int candidate = dp[k][u] + V[to] - cost;
                if (candidate > dp[k + 1][to]) {
                    dp[k + 1][to] = candidate;
                    parent[k + 1][to] = {u, k};
                }
            }
        }
    }

    // Select the best result among all allowed number of edges.
    int best_net = INF_NEG;
    int best_edges = -1;
    for (int k = 0; k <= K; ++k) {
        if (dp[k][end_city] > best_net) {
            best_net = dp[k][end_city];
            best_edges = k;
        } else if (dp[k][end_city] == best_net && best_net != INF_NEG && k < best_edges) {
            best_edges = k;
        }
    }

    if (best_net == INF_NEG) {
        return {std::vector<int>(), INF_NEG};
    }

    // Reconstruct the path from end_city using the parent pointers.
    std::vector<int> path;
    int current_node = end_city;
    int current_edge_count = best_edges;
    while (current_edge_count >= 0) {
        path.push_back(current_node);
        if (current_edge_count == 0)
            break;
        auto prev = parent[current_edge_count][current_node];
        current_node = prev.first;
        current_edge_count = prev.second;
    }
    std::reverse(path.begin(), path.end());
    return {path, best_net};
}

} // namespace ancient_cipher