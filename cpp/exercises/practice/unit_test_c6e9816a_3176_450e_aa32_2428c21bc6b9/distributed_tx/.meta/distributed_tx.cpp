#include "distributed_tx.h"
#include <vector>
#include <tuple>
#include <queue>
#include <limits>

namespace distributed_tx {

double expected_transaction_cost(int N,
                                 const std::vector<std::tuple<int, int, int>>& edges,
                                 const std::vector<double>& failure_probability,
                                 const std::vector<int>& prep_cost,
                                 const std::vector<int>& commit_cost) {
    if (N <= 0) return 0.0;
    
    // Build graph adjacency list
    std::vector<std::vector<std::pair<int, int>>> adj(N);
    for (const auto &edge : edges) {
        int u, v, w;
        std::tie(u, v, w) = edge;
        adj[u].push_back({v, w});
        adj[v].push_back({u, w});
    }
    
    // Dijkstra's algorithm from the coordinator (node 0)
    const int INF = std::numeric_limits<int>::max();
    std::vector<int> dist(N, INF);
    dist[0] = 0;
    using pii = std::pair<int, int>;
    std::priority_queue<pii, std::vector<pii>, std::greater<pii>> pq;
    pq.push({0, 0});
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        for (const auto &neighbor : adj[u]) {
            int v = neighbor.first;
            int weight = neighbor.second;
            if (d + weight < dist[v]) {
                dist[v] = d + weight;
                pq.push({dist[v], v});
            }
        }
    }
    
    // Calculate network latency cost (round-trip cost for each microservice except the coordinator)
    long long total_network = 0;
    for (int i = 1; i < N; i++) {
        if (dist[i] != INF) {
            total_network += 2LL * dist[i];
        }
    }
    
    // Calculate total preparation cost for microservices (services 1 to N-1)
    long long total_prep = 0;
    for (const auto &cost : prep_cost) {
        total_prep += cost;
    }
    
    // Calculate total commit cost and overall commit probability
    long long total_commit = 0;
    double commit_prob = 1.0;
    for (const auto &cost : commit_cost) {
        total_commit += cost;
    }
    for (const auto &prob : failure_probability) {
        commit_prob *= (1.0 - prob);
    }
    double expected_commit_cost = total_commit * commit_prob;
    
    // Total expected cost is sum of network cost, preparation cost and expected commit cost
    double total_cost = static_cast<double>(total_network) + static_cast<double>(total_prep) + expected_commit_cost;
    return total_cost;
}

} // namespace distributed_tx