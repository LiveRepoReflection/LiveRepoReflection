#include "optimal_traffic.h"
#include <vector>
#include <tuple>
#include <queue>
#include <algorithm>
#include <limits>

using namespace std;
 
namespace {

const int INF = 1000000000;
 
struct Edge {
    int to;
    int rev;
    int cap;
};
 
struct Dinic {
    vector<vector<Edge>> graph;
    vector<int> level, ptr;
    int source, sink;
 
    Dinic(int n, int source, int sink) : graph(n), level(n), ptr(n), source(source), sink(sink) { }
 
    void add_edge(int s, int t, int cap) {
        Edge a = {t, (int)graph[t].size(), cap};
        Edge b = {s, (int)graph[s].size(), 0};
        graph[s].push_back(a);
        graph[t].push_back(b);
    }
 
    bool bfs() {
        fill(level.begin(), level.end(), -1);
        level[source] = 0;
        queue<int> q;
        q.push(source);
 
        while(!q.empty()){
            int u = q.front();
            q.pop();
            for(auto &e: graph[u]){
                if(level[e.to] < 0 && e.cap){
                    level[e.to] = level[u] + 1;
                    q.push(e.to);
                }
            }
        }
        return level[sink] != -1;
    }
 
    int dfs(int u, int pushed) {
        if(!pushed) return 0;
        if(u == sink) return pushed;
 
        for(int &cid = ptr[u]; cid < (int)graph[u].size(); cid++){
            Edge &e = graph[u][cid];
            if(level[u] + 1 != level[e.to] || !e.cap)
                continue;
            int tr = dfs(e.to, min(pushed, e.cap));
            if(tr){
                e.cap -= tr;
                graph[e.to][e.rev].cap += tr;
                return tr;
            }
        }
        return 0;
    }
 
    int max_flow() {
        int flow = 0;
        while(bfs()){
            fill(ptr.begin(), ptr.end(), 0);
            while (int pushed = dfs(source, INF)) {
                flow += pushed;
            }
        }
        return flow;
    }
};
 
} // end anonymous namespace
 
namespace optimal_traffic {
 
// Function: earliest_arrival
// Input parameters:
//   num_intersections: number of intersections (nodes)
//   roads: vector of tuples (source, destination, initial_capacity, travel_time)
//   start_intersections: starting intersections for each car (each car contributes one unit of flow)
//   destination: destination intersection for all cars
//   capacity_updates: vector of tuples (source, destination, start_time, end_time, new_capacity)
 
int earliest_arrival(int num_intersections,
                     const vector<tuple<int, int, int, int>> &roads,
                     const vector<int> &start_intersections,
                     int destination,
                     const vector<tuple<int, int, int, int, int>> &capacity_updates) {
    // Determine total number of cars from start_intersections (with possible duplicates)
    int total_cars = start_intersections.size();
 
    // Set maximum time to consider. Using 1200 as an upper bound (updates up to 1000 and travel times up to 100)
    const int max_time = 1200;
 
    // Precompute dynamic capacity for each road for times 0 .. max_time.
    // For each road in roads vector, store a vector<int> of capacity for time t.
    int num_roads = roads.size();
    vector<vector<int>> road_caps(num_roads, vector<int>(max_time + 1, 0));
 
    for (int i = 0; i < num_roads; i++) {
        int ru, rv, base_cap, travel_time;
        tie(ru, rv, base_cap, travel_time) = roads[i];
        for (int t = 0; t <= max_time; t++) {
            road_caps[i][t] = base_cap;
        }
    }
 
    // Apply capacity updates in order; latest update overwrites previous ones.
    for (const auto &upd : capacity_updates) {
        int u, v, start_time, end_time, new_cap;
        tie(u, v, start_time, end_time, new_cap) = upd;
        // For each road matching (u,v), update capacity in time interval [start_time, end_time]
        for (int i = 0; i < num_roads; i++) {
            int ru, rv, base_cap, travel_time;
            tie(ru, rv, base_cap, travel_time) = roads[i];
            if (ru == u && rv == v) {
                int st = max(0, start_time);
                int en = min(max_time, end_time);
                for (int t = st; t <= en; t++) {
                    road_caps[i][t] = new_cap;
                }
            }
        }
    }
 
    // Count frequency of starting intersections.
    vector<int> start_count(num_intersections, 0);
    for (int s : start_intersections) {
        start_count[s]++;
    }
 
    // Binary search for the minimal time T such that all cars can reach destination.
    int low = 0, high = max_time, ans = -1;
    while(low <= high){
        int mid = (low + high) / 2;
        // Build time-expanded network from time 0 to mid.
        // For each intersection i at time t, node index = i * (mid+1) + t.
        int layers = mid + 1;
        int base_nodes = num_intersections * layers;
        // Additional nodes: super source and super sink.
        int source_node = base_nodes;
        int sink_node = base_nodes + 1;
        int total_nodes = base_nodes + 2;
 
        Dinic dinic(total_nodes, source_node, sink_node);
 
        // Add waiting edges for each intersection: from (i, t) to (i, t+1) with capacity INF.
        for (int i = 0; i < num_intersections; i++) {
            for (int t = 0; t < mid; t++) {
                int u = i * layers + t;
                int v = i * layers + (t + 1);
                dinic.add_edge(u, v, INF);
            }
        }
 
        // Add road edges.
        for (int r = 0; r < num_roads; r++) {
            int ru, rv, base_cap, travel_time;
            tie(ru, rv, base_cap, travel_time) = roads[r];
            // For each possible departure time t such that arrival time <= mid.
            for (int t = 0; t + travel_time <= mid; t++) {
                int u = ru * layers + t;
                int v = rv * layers + (t + travel_time);
                int cap = road_caps[r][t];
                if(cap > 0){
                    dinic.add_edge(u, v, cap);
                }
            }
        }
 
        // Connect super source to starting positions at time 0.
        for (int i = 0; i < num_intersections; i++) {
            if(start_count[i] > 0){
                int node = i * layers + 0;
                dinic.add_edge(source_node, node, start_count[i]);
            }
        }
 
        // Connect destination nodes at any time (0 to mid) to super sink.
        for (int t = 0; t <= mid; t++) {
            int node = destination * layers + t;
            dinic.add_edge(node, sink_node, INF);
        }
 
        int flow = dinic.max_flow();
        if(flow >= total_cars){
            ans = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
 
    return ans;
}
 
} // namespace optimal_traffic