#include "network_flow.h"
#include <vector>
#include <queue>
#include <map>
#include <tuple>
#include <algorithm>
#include <limits>
#include <cassert>

using std::vector;
using std::queue;
using std::map;
using std::tuple;
using std::get;

namespace network_flow {

struct Request {
    int source;
    int destination;
    int demand;
    int allocated;
};

static int n = 0;
static vector<vector<int>> original_cap; // original capacities (undirected graph)
static map<int, Request> activeRequests;  // request_id -> Request

// Helper function: perform BFS in residual network to find an augmenting path.
// Returns true if path found, and fills parent vector with the path.
static bool bfs(const vector<vector<int>>& capacity, int s, int t, vector<int>& parent) {
    int N = capacity.size();
    vector<bool> visited(N, false);
    queue<int> q;
    q.push(s);
    visited[s] = true;
    parent.assign(N, -1);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v = 0; v < N; v++) {
            if (!visited[v] && capacity[u][v] > 0) {
                parent[v] = u;
                visited[v] = true;
                if (v == t)
                    return true;
                q.push(v);
            }
        }
    }
    return false;
}

// Edmonds-Karp to compute flow from s to t but not exceeding "limit".
static int max_flow_with_limit(int s, int t, int limit, vector<vector<int>>& cap) {
    int flow = 0;
    int N = cap.size();
    vector<int> parent(N, -1);
    while (flow < limit && bfs(cap, s, t, parent)) {
        int path_flow = limit - flow; // maximum we can add in this iteration
        int v = t;
        while (v != s) {
            int u = parent[v];
            path_flow = std::min(path_flow, cap[u][v]);
            v = u;
        }
        v = t;
        while (v != s) {
            int u = parent[v];
            cap[u][v] -= path_flow;
            cap[v][u] += path_flow;
            v = u;
        }
        flow += path_flow;
    }
    return flow;
}

// Recompute flow allocations for all active requests in increasing order of request id.
// This function resets the residual capacities to original capacities and then for each request,
// computes its allocated flow using max flow with limit = demand.
static void recompute_flows() {
    // Reset capacities from original_cap
    vector<vector<int>> current_cap = original_cap;
    // Sort active requests by request_id (map keys are sorted already)
    for (auto& kv : activeRequests) {
        Request& req = kv.second;
        int allocated = max_flow_with_limit(req.source, req.destination, req.demand, current_cap);
        req.allocated = allocated;
    }
}

void init_network(int N, const vector<tuple<int, int, int>>& edges) {
    n = N;
    original_cap.assign(n, vector<int>(n, 0));
    // For each undirected edge, add capacity for both directions.
    for (const auto& edge : edges) {
        int u, v, cap;
        std::tie(u, v, cap) = edge;
        assert(u >= 0 && u < n && v >= 0 && v < n);
        original_cap[u][v] += cap;
        original_cap[v][u] += cap;
    }
    activeRequests.clear();
}

void add_request(int request_id, int source, int destination, int demand) {
    if(source < 0 || source >= n || destination < 0 || destination >= n) {
        return;
    }
    Request req;
    req.source = source;
    req.destination = destination;
    req.demand = demand;
    req.allocated = 0;
    activeRequests[request_id] = req;
    recompute_flows();
}

void remove_request(int request_id) {
    activeRequests.erase(request_id);
    recompute_flows();
}

int query_request(int request_id) {
    auto it = activeRequests.find(request_id);
    if (it == activeRequests.end()) {
        return 0;
    }
    return it->second.allocated;
}

} // namespace network_flow