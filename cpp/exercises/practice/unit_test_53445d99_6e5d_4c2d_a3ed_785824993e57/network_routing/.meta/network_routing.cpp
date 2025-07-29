#include "network_routing.h"
#include <vector>
#include <tuple>
#include <limits>
#include <queue>
#include <algorithm>
#include <climits>

using std::vector;
using std::tuple;
using std::pair;

static int N = 0;
static int curr_time = 1;
static vector<vector<vector<pair<int,int>>>> events;
static vector<vector<int>> adjList;

static int get_effective_latency(int u, int v, int query_timestamp) {
    const vector<pair<int,int>>& ev = events[u][v];
    if(ev.empty()) return -1;
    int lo = 0, hi = ev.size() - 1, res_index = -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if(ev[mid].first <= query_timestamp) {
            res_index = mid;
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    if(res_index == -1) return -1;
    int lat = ev[res_index].second;
    if(lat == -1) return -1;
    return lat;
}

void init(int n, const vector<tuple<int,int,int>>& initial_latencies) {
    N = n;
    events.clear();
    events.resize(N, vector<vector<pair<int,int>>>(N));
    adjList.clear();
    adjList.resize(N);
    curr_time = 1;  
    for (const auto& edge: initial_latencies) {
        int u, v, latency;
        std::tie(u, v, latency) = edge;
        events[u][v].push_back({0, latency});
        events[v][u].push_back({0, latency});
        if(std::find(adjList[u].begin(), adjList[u].end(), v) == adjList[u].end())
            adjList[u].push_back(v);
        if(std::find(adjList[v].begin(), adjList[v].end(), u) == adjList[v].end())
            adjList[v].push_back(u);
    }
}

void update_latency(int u, int v, int latency) {
    if(events[u][v].empty()) {
        if(std::find(adjList[u].begin(), adjList[u].end(), v) == adjList[u].end())
            adjList[u].push_back(v);
        if(std::find(adjList[v].begin(), adjList[v].end(), u) == adjList[v].end())
            adjList[v].push_back(u);
    }
    events[u][v].push_back({curr_time, latency});
    events[v][u].push_back({curr_time, latency});
    curr_time++;
}

std::vector<int> find_shortest_path(int start_node, int end_node, int query_timestamp) {
    if(start_node == end_node) return {start_node};
    const int INF = std::numeric_limits<int>::max();
    vector<int> dist(N, INF);
    vector<int> prev(N, -1);
    typedef pair<int, int> NodeDist;
    std::priority_queue<NodeDist, vector<NodeDist>, std::greater<NodeDist>> pq;
    dist[start_node] = 0;
    pq.push({0, start_node});
    while(!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if(d > dist[u]) continue;
        if(u == end_node) break;
        for (int v: adjList[u]) {
            int edge_latency = get_effective_latency(u, v, query_timestamp);
            if(edge_latency == -1) continue;
            if(dist[u] != INF && dist[u] + edge_latency < dist[v]) {
                dist[v] = dist[u] + edge_latency;
                prev[v] = u;
                pq.push({dist[v], v});
            }
        }
    }
    if(dist[end_node] == INF) {
        return vector<int>();
    }
    vector<int> path;
    for (int cur = end_node; cur != -1; cur = prev[cur])
        path.push_back(cur);
    std::reverse(path.begin(), path.end());
    return path;
}