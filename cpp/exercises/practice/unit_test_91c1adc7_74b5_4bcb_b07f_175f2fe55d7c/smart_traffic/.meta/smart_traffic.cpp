#include "smart_traffic.h"
#include <vector>
#include <tuple>
#include <queue>
#include <algorithm>
#include <climits>

using std::vector;
using std::tuple;
using std::get;
using std::max;

namespace {

// Dinic's max flow implementation
struct Edge {
    int to, rev;
    int cap;
};

struct Dinic {
    int N;
    vector<vector<Edge>> graph;
    vector<int> level, it;
    
    Dinic(int N): N(N), graph(N), level(N), it(N) { }
    
    void add_edge(int s, int t, int cap) {
        Edge a = {t, (int)graph[t].size(), cap};
        Edge b = {s, (int)graph[s].size(), 0};
        graph[s].push_back(a);
        graph[t].push_back(b);
    }
    
    bool bfs(int s, int t) {
        std::fill(level.begin(), level.end(), -1);
        level[s] = 0;
        std::queue<int> q;
        q.push(s);
        while (!q.empty()) {
            int u = q.front();
            q.pop();
            for (const Edge &e : graph[u]) {
                if (e.cap > 0 && level[e.to] < 0) {
                    level[e.to] = level[u] + 1;
                    q.push(e.to);
                }
            }
        }
        return level[t] >= 0;
    }
    
    int dfs(int u, int t, int flow) {
        if (!flow) return 0;
        if (u == t) return flow;
        for (int &i = it[u]; i < (int)graph[u].size(); i++) {
            Edge &e = graph[u][i];
            if (e.cap > 0 && level[e.to] == level[u] + 1) {
                int pushed = dfs(e.to, t, std::min(flow, e.cap));
                if (pushed) {
                    e.cap -= pushed;
                    graph[e.to][e.rev].cap += pushed;
                    return pushed;
                }
            }
        }
        return 0;
    }
    
    int max_flow(int s, int t) {
        int flow = 0;
        while (bfs(s, t)) {
            std::fill(it.begin(), it.end(), 0);
            while (int pushed = dfs(s, t, INT_MAX))
                flow += pushed;
        }
        return flow;
    }
};

} // anonymous namespace

namespace smart_traffic {

int calculate_optimal_flow(int N, int source, int sink,
    const vector<tuple<int, int, int, int, int, int>> &roads) {

    // If source and sink are same, no flow is needed.
    if(source == sink)
        return 0;
    
    // Identify indices of roads that have a toll booth (toll_booth_cost > 0)
    vector<int> tollIndices;
    for (int i = 0; i < (int)roads.size(); i++) {
        int toll_cost = std::get<4>(roads[i]);
        if (toll_cost > 0)
            tollIndices.push_back(i);
    }
    
    int tollCount = tollIndices.size();
    int bestNet = 0;
    
    // Enumerate over all possible disabling combinations for toll roads.
    // Each bit in mask corresponds to one toll road in tollIndices.
    // For non-toll roads, the effective capacity = capacity - current_flow.
    // For toll roads:
    //    if not disabled, effective capacity = max(0, capacity - current_flow - toll_booth_cost).
    //    if disabled, effective capacity = capacity - current_flow.
    // The penalty for disabling a toll booth is subtracted from the final flow.
    
    // We use bitmask enumeration over tollCount toll roads.
    int totalMasks = 1 << tollCount;
    for (int mask = 0; mask < totalMasks; mask++) {
        int penalty = 0;
        Dinic dinic(N);
        for (int i = 0; i < (int)roads.size(); i++) {
            int u = std::get<0>(roads[i]);
            int v = std::get<1>(roads[i]);
            int capacity = std::get<2>(roads[i]);
            int current_flow = std::get<3>(roads[i]);
            int toll_cost = std::get<4>(roads[i]);
            int disable_penalty = std::get<5>(roads[i]);
            int effective_cap = 0;
            
            if (toll_cost == 0) {
                effective_cap = capacity - current_flow;
            } else {
                // This is a toll road.
                // Check if this road is disabled under the current mask.
                bool disable = false;
                // Find the index of this toll road in tollIndices.
                auto it = std::find(tollIndices.begin(), tollIndices.end(), i);
                if(it != tollIndices.end()){
                    int index = it - tollIndices.begin();
                    if(mask & (1 << index)) {
                        disable = true;
                        penalty += disable_penalty;
                    }
                }
                if (disable) {
                    effective_cap = capacity - current_flow;
                } else {
                    effective_cap = capacity - current_flow - toll_cost;
                }
            }
            if (effective_cap < 0) effective_cap = 0;
            dinic.add_edge(u, v, effective_cap);
        }
        int flow = dinic.max_flow(source, sink);
        int net = flow - penalty;
        bestNet = max(bestNet, net);
    }
    
    return bestNet;
}

} // namespace smart_traffic