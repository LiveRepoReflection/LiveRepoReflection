#include "network_optimize.h"
#include <vector>
#include <stdexcept>
#include <limits>
#include <algorithm>

namespace network_optimize {

const int INF = 1000000000;

static void compute_baseline(int N, const std::vector<std::vector<int>>& input,
                             std::vector<std::vector<int>>& dist) {
    dist.assign(N, std::vector<int>(N, INF));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (i == j) {
                dist[i][j] = 0;
            } else if (input[i][j] != -1) {
                dist[i][j] = input[i][j];
            }
        }
    }
    // Floyd-Warshall algorithm for all pairs shortest paths
    for (int k = 0; k < N; ++k) {
        for (int i = 0; i < N; ++i) {
            if(dist[i][k] == INF) continue;
            for (int j = 0; j < N; ++j) {
                if(dist[k][j] == INF) continue;
                if(dist[i][j] > dist[i][k] + dist[k][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
}

static void generate_combinations(int start, int K, int N, std::vector<int>& current,
                                  std::vector<std::vector<int>>& allCombos) {
    if (K == 0) {
        allCombos.push_back(current);
        return;
    }
    for (int i = start; i <= N - K; ++i) {
        current.push_back(i);
        generate_combinations(i + 1, K - 1, N, current, allCombos);
        current.pop_back();
    }
}

double optimize_network(int N, const std::vector<std::vector<int>>& adjMatrix, int K) {
    // Precompute baseline shortest paths using Floyd-Warshall
    std::vector<std::vector<int>> baseline;
    compute_baseline(N, adjMatrix, baseline);

    // Helper lambda to decide if the network (for given pair distances) is fully connected.
    auto check_connected = [&](const std::vector<std::vector<int>>& distances) -> bool {
        for (int i = 0; i < N; ++i) {
            for (int j = i+1; j < N; ++j) {
                if (distances[i][j] == INF) {
                    return false;
                }
            }
        }
        return true;
    };

    // If K is 0, then no accelerator improvement is possible.
    if (K == 0) {
        if (!check_connected(baseline)) {
            throw std::invalid_argument("Network is disconnected");
        }
        long long sum = 0;
        int count = 0;
        for (int i = 0; i < N; ++i) {
            for (int j = i + 1; j < N; ++j) {
                sum += baseline[i][j];
                ++count;
            }
        }
        return static_cast<double>(sum) / count;
    }

    // Generate all possible combinations of accelerator nodes of size K.
    std::vector<std::vector<int>> combos;
    std::vector<int> current;
    generate_combinations(0, K, N, current, combos);

    double bestAvg = std::numeric_limits<double>::infinity();
    bool found = false;

    // Precompute direct edge matrix for accelerator usage.
    // Convert -1 to INF for ease of use.
    std::vector<std::vector<int>> direct = adjMatrix;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if(i == j) continue;
            if(direct[i][j] == -1) {
                direct[i][j] = INF;
            }
        }
    }

    // For each accelerator combination S, compute final latency for each pair.
    for (const auto& accelSet : combos) {
        long long total = 0;
        int pairs = 0;
        bool valid = true;
        // For every unordered pair i,j, compute minimum distance.
        for (int i = 0; i < N && valid; ++i) {
            for (int j = i + 1; j < N && valid; ++j) {
                int candidate = baseline[i][j];
                // Try improving the distance using one of the accelerator nodes.
                for (int a : accelSet) {
                    if (direct[i][a] != INF && direct[a][j] != INF) {
                        candidate = std::min(candidate, direct[i][a] + direct[a][j]);
                    }
                }
                if (candidate == INF) {
                    valid = false;
                    break;
                }
                total += candidate;
                ++pairs;
            }
        }
        if (valid && pairs > 0) {
            double avg = static_cast<double>(total) / pairs;
            bestAvg = std::min(bestAvg, avg);
            found = true;
        }
    }
    if (!found) {
        throw std::invalid_argument("Network is disconnected with given accelerators");
    }
    return bestAvg;
}

}  // namespace network_optimize