#include "network_deploy.h"
#include <vector>
#include <tuple>
#include <cmath>
#include <limits>
#include <algorithm>

namespace network_deploy {

// Helper function: Manhattan distance between two points.
inline int manhattan_distance(int x1, int y1, int x2, int y2) {
    return std::abs(x1 - x2) + std::abs(y1 - y2);
}

// Computes the total number of covered cells within the grid given a subset
// of base stations, represented by bitmask (where bit i set indicates baseStations[i] is deployed).
// A cell (i, j) is covered if for the closest deployed base station (in terms of Manhattan distance)
// the effective signal (station power minus distance) is at least T.
int compute_coverage(int N, int M, const std::vector<std::tuple<int, int, int, int>>& baseStations, int T, int subset) {
    int coverage = 0;
    // For each cell in the grid.
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < M; j++) {
            int bestDistance = std::numeric_limits<int>::max();
            int candidateIndex = -1;
            // Find the deployed base station that is closest to (i, j)
            for (size_t k = 0; k < baseStations.size(); k++) {
                if (subset & (1 << k)) {
                    int x, y, p, r;
                    std::tie(x, y, p, r) = baseStations[k];
                    int d = manhattan_distance(i, j, x, y);
                    if (d < bestDistance) {
                        bestDistance = d;
                        candidateIndex = k;
                    }
                }
            }
            if (candidateIndex != -1) {
                int x, y, p, r;
                std::tie(x, y, p, r) = baseStations[candidateIndex];
                int effectiveSignal = p - bestDistance;
                if (effectiveSignal >= T) {
                    coverage++;
                }
            }
        }
    }
    return coverage;
}

// Computes interference score for the deployed base stations in the given subset.
// For every pair of deployed base stations if the Manhattan distance between them
// is less than or equal to the sum of their interference radii, interference adds p1 * p2.
int compute_interference(const std::vector<std::tuple<int, int, int, int>>& baseStations, int subset) {
    int interference = 0;
    int n = baseStations.size();
    for (int i = 0; i < n; i++) {
        if (!(subset & (1 << i))) continue;
        int x1, y1, p1, r1;
        std::tie(x1, y1, p1, r1) = baseStations[i];
        for (int j = i + 1; j < n; j++) {
            if (!(subset & (1 << j))) continue;
            int x2, y2, p2, r2;
            std::tie(x2, y2, p2, r2) = baseStations[j];
            int d = manhattan_distance(x1, y1, x2, y2);
            if (d <= (r1 + r2)) {
                interference += (p1 * p2);
            }
        }
    }
    return interference;
}

// The objective function balances coverage and interference.
// We define objective = coverage - interference.
// In a real-world scenario, a scaling factor may be used; here we use a constant weight of 1.
int compute_objective(int coverage, int interference) {
    return coverage - interference;
}

std::vector<int> optimal_network_deploy(int N, int M, const std::vector<std::tuple<int, int, int, int>>& baseStations, int T) {
    int K = baseStations.size();
    int bestObjective = std::numeric_limits<int>::min();
    int bestCoverage = -1;
    int bestSubset = 0;

    // Iterate through all possible subsets of candidate base stations.
    // Since K <= 20, 2^K is feasible.
    int totalSubsets = 1 << K;
    for (int subset = 0; subset < totalSubsets; subset++) {
        // Compute coverage and interference for this subset.
        int coverage = compute_coverage(N, M, baseStations, T, subset);
        int interference = compute_interference(baseStations, subset);
        int objective = compute_objective(coverage, interference);
        
        // Choose the subset with the best objective.
        // In case of a tie in objective, choose one with higher coverage.
        if (objective > bestObjective || (objective == bestObjective && coverage > bestCoverage)) {
            bestObjective = objective;
            bestCoverage = coverage;
            bestSubset = subset;
        }
    }
    
    // Prepare the list of indices from bestSubset.
    std::vector<int> result;
    for (int i = 0; i < K; i++) {
        if (bestSubset & (1 << i)) {
            result.push_back(i);
        }
    }
    // Sort the result vector for consistency.
    std::sort(result.begin(), result.end());
    return result;
}

}  // namespace network_deploy