#include "bottleneck_paths.h"
#include <vector>
#include <tuple>
#include <queue>
#include <limits>
#include <algorithm>
#include <set>
#include <utility>

using namespace std;

namespace bottleneck_paths {

struct NodeState {
    int cap;
    int node;
    // For max-heap; higher bottleneck capacity has higher priority.
    bool operator<(const NodeState& other) const {
        return cap < other.cap;
    }
};

vector<Result> compute_bottleneck_paths(int N, const vector<tuple<int, int, int>>& edges, const vector<int>& srcs) {
    // Build graph: 1-indexed; each entry: (neighbor, capacity)
    vector<vector<pair<int, int>>> graph(N + 1);
    for (const auto& edge : edges) {
        int u, v, cap;
        std::tie(u, v, cap) = edge;
        graph[u].push_back({v, cap});
    }
    
    // best[i]: best (maximum) bottleneck capacity achievable from any source to node i.
    vector<int> best(N + 1, 0);
    // origin[i]: set of source nodes contributing to best[i]
    vector<set<int>> origin(N + 1);
    
    // Priority queue: using max-heap based on bottleneck capacity
    priority_queue<NodeState> pq;
    
    // Use a set to track the unique source nodes.
    set<int> unique_sources;
    for (int s : srcs) {
        if (unique_sources.find(s) == unique_sources.end()) {
            unique_sources.insert(s);
            best[s] = std::numeric_limits<int>::max();
            origin[s].insert(s);
            pq.push(NodeState{best[s], s});
        }
    }
    
    // Multi-source Dijkstra-like traversal for maximum bottleneck paths.
    while (!pq.empty()) {
        NodeState cur = pq.top();
        pq.pop();
        
        if (cur.cap != best[cur.node])
            continue;  // Skip outdated state
        
        for (const auto& edge : graph[cur.node]) {
            int nxt = edge.first;
            int edge_cap = edge.second;
            int new_cap = std::min(cur.cap, edge_cap);
            if (new_cap > best[nxt]) {
                best[nxt] = new_cap;
                origin[nxt] = origin[cur.node];  // Copy current source set.
                pq.push(NodeState{new_cap, nxt});
            } else if (new_cap == best[nxt] && new_cap != 0) {
                // Merge the source sets if new sources are found.
                bool updated = false;
                for (int s : origin[cur.node]) {
                    if (origin[nxt].find(s) == origin[nxt].end()) {
                        origin[nxt].insert(s);
                        updated = true;
                    }
                }
                if (updated) {
                    pq.push(NodeState{new_cap, nxt});
                }
            }
        }
    }
    
    // Prepare results for nodes that are not source cities.
    vector<Result> results;
    for (int node = 1; node <= N; node++) {
        if (unique_sources.find(node) != unique_sources.end())
            continue;  // Skip source nodes in the result
        
        Result res;
        res.destination = node;
        res.max_bottleneck_capacity = best[node];
        res.sources.assign(origin[node].begin(), origin[node].end());
        results.push_back(res);
    }
    
    return results;
}

}  // namespace bottleneck_paths