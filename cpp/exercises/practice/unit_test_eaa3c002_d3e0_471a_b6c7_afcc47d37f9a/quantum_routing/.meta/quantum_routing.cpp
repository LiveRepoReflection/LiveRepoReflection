#include "quantum_routing.h"
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

using std::vector;
using std::priority_queue;
using std::pair;
using std::make_pair;
using std::numeric_limits;

std::vector<int> quantumRouting(int N, const vector<vector<double>>& channel_probabilities, int S, int D, int max_attempts) {
    if (S == D) {
        return vector<int>{S};
    }
    
    const double INF = numeric_limits<double>::infinity();
    vector<double> dist(N, INF);
    vector<int> parent(N, -1);
    dist[S] = 0.0;

    // Priority queue to get the node with the smallest expected cost.
    priority_queue<pair<double, int>, vector<pair<double, int>>, std::greater<pair<double, int>>> pq;
    pq.push(make_pair(0.0, S));

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u])
            continue;
        if (u == D)
            break;
        for (int v = 0; v < N; ++v) {
            if (u == v)
                continue;
            double p = channel_probabilities[u][v];
            if (p <= 0.0)
                continue;
            // The expected number of attempts for a successful teleportation is 1/p.
            double weight = 1.0 / p;
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                parent[v] = u;
                pq.push(make_pair(dist[v], v));
            }
        }
    }

    if (dist[D] == INF || dist[D] > max_attempts) {
        return vector<int>(); // No valid path found within the allowed max_attempts.
    }
    
    // Reconstruct the path from destination D to source S.
    vector<int> path;
    int cur = D;
    while (cur != -1) {
        path.push_back(cur);
        cur = parent[cur];
    }
    std::reverse(path.begin(), path.end());
    return path;
}