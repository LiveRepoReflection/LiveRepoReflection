#include "network_capacity.h"
#include <vector>
#include <cmath>
#include <queue>
#include <limits>
#include <algorithm>

using std::vector;
using std::priority_queue;
using std::pair;
using std::make_pair;
using std::numeric_limits;
using std::sort;
using std::unique;
using std::greater;
using std::exp;
using std::log;

namespace network_capacity {

double max_guaranteed_bandwidth(int N, const vector<Edge>& edges, int S, int D) {
    // Extract distinct capacity candidates from edges.
    vector<int> capacity_candidates;
    for (const auto& e : edges) {
        capacity_candidates.push_back(e.capacity);
    }
    sort(capacity_candidates.begin(), capacity_candidates.end());
    capacity_candidates.erase(unique(capacity_candidates.begin(), capacity_candidates.end()), capacity_candidates.end());
    // Process candidate capacities in descending order.
    sort(capacity_candidates.begin(), capacity_candidates.end(), greater<int>());

    double best = 0.0;
    // For each capacity threshold L, restrict to edges that can support at least L.
    for (int L : capacity_candidates) {
        // Build the subgraph as an adjacency list.
        vector<vector<pair<int, double>>> graph(N);
        for (const auto& e : edges) {
            if (e.capacity >= L) {
                // Calculate reliability: if failure_probability is 0 then edge is fully reliable.
                double reliability = (e.failure_probability == 0.0) ? 1.0 : (1.0 - e.failure_probability);
                graph[e.u].push_back(make_pair(e.v, reliability));
                graph[e.v].push_back(make_pair(e.u, reliability));
            }
        }
        // Use Dijkstra's algorithm on transformed weights to maximize product reliability.
        // Transform: for an edge with reliability r, use weight = -log(r).
        vector<double> dist(N, numeric_limits<double>::infinity());
        dist[S] = 0.0;
        typedef pair<double, int> PDI;
        priority_queue<PDI, vector<PDI>, greater<PDI>> pq;
        pq.push(make_pair(0.0, S));
        while (!pq.empty()) {
            auto current = pq.top();
            pq.pop();
            double d = current.first;
            int u = current.second;
            if (d > dist[u] + 1e-12) continue;
            if (u == D) break;
            for (const auto &edge : graph[u]) {
                int v = edge.first;
                double reliability = edge.second;
                double weight = -log(reliability);
                if (dist[u] + weight < dist[v] - 1e-12) {
                    dist[v] = dist[u] + weight;
                    pq.push(make_pair(dist[v], v));
                }
            }
        }
        if (dist[D] == numeric_limits<double>::infinity())
            continue;
        double prod = exp(-dist[D]); // Maximum product reliability for path under threshold L.
        double candidate = L * prod;
        if (candidate > best)
            best = candidate;
    }
    return best;
}

} // namespace network_capacity