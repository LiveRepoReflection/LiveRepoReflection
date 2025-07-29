#include "network_routing.h"
#include <vector>
#include <queue>
#include <limits>

namespace network_routing {

struct Edge {
    int to;
    int weight;
};

void solve(std::istream &in, std::ostream &out) {
    int N, M;
    in >> N >> M;
    std::vector<std::vector<Edge>> graph(N + 1);
    for (int i = 0; i < M; i++) {
        int u, v, w;
        in >> u >> v >> w;
        graph[u].push_back({v, w});
        graph[v].push_back({u, w});
    }

    int Q;
    in >> Q;
    // Group queries by source node.
    std::vector<std::vector<std::pair<int, int>>> queries(N + 1);
    std::vector<int> answers(Q, -1);
    // Store each query with its index.
    std::vector<int> srcs(Q), dests(Q);
    for (int i = 0; i < Q; i++) {
        int s, d;
        in >> s >> d;
        srcs[i] = s;
        dests[i] = d;
        queries[s].push_back({i, d});
    }

    // For each source that has at least one query, perform Dijkstra's algorithm.
    for (int s = 1; s <= N; s++) {
        if (queries[s].empty()) continue;
        const int INF = std::numeric_limits<int>::max();
        std::vector<int> dist(N + 1, INF);
        typedef std::pair<int, int> pii;
        std::priority_queue<pii, std::vector<pii>, std::greater<pii>> pq;
        dist[s] = 0;
        pq.push({0, s});
        while (!pq.empty()) {
            auto current = pq.top();
            pq.pop();
            int d = current.first;
            int node = current.second;
            if (d > dist[node]) continue;
            for (const auto &edge : graph[node]) {
                int new_dist = d + edge.weight;
                if (new_dist < dist[edge.to]) {
                    dist[edge.to] = new_dist;
                    pq.push({new_dist, edge.to});
                }
            }
        }
        // Answer the queries for this source.
        for (const auto &query : queries[s]) {
            int idx = query.first;
            int dest = query.second;
            if (dist[dest] == INF)
                answers[idx] = -1;
            else
                answers[idx] = dist[dest];
        }
    }

    // Output the answers in the order of the queries.
    for (int i = 0; i < Q; i++) {
        out << answers[i] << "\n";
    }
}

}  // namespace network_routing