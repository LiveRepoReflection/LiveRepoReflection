#include "traffic_router.h"
#include <vector>
#include <queue>
#include <limits>
#include <cmath>
#include <iomanip>

namespace traffic_router {

struct Edge {
    int u, v;
    double capacity;
    double base_time;
};

struct Trip {
    int source;
    int dest;
    double demand;
};

struct NodeState {
    double dist;
    int node;
    // For priority_queue ordering
    bool operator>(const NodeState &other) const {
        return dist > other.dist;
    }
};

void solve(std::istream &in, std::ostream &out) {
    int N, M;
    in >> N >> M;
    
    std::vector<Edge> edges(M);
    // Build graph structure: for each node, list of edge indices leaving it.
    std::vector<std::vector<int>> graph(N);
    for (int i = 0; i < M; i++) {
        int u, v;
        double cap, base;
        in >> u >> v >> cap >> base;
        edges[i] = {u, v, cap, base};
        graph[u].push_back(i);
    }
    
    int K;
    in >> K;
    std::vector<Trip> trips(K);
    for (int i = 0; i < K; i++) {
        int s, d;
        double demand;
        in >> s >> d >> demand;
        trips[i] = {s, d, demand};
    }
    
    double congestion_factor, exponent;
    in >> congestion_factor >> exponent;
    
    // Initialize flows on each edge to 0
    std::vector<double> flow(M, 0.0);
    
    // Parameters for iterative algorithm (Frank-Wolfe approach)
    const int max_iter = 1000;
    const double tolerance = 1e-6;
    
    // Main iterative loop
    for (int iter = 0; iter < max_iter; iter++) {
        // Calculate current travel times on each edge
        std::vector<double> travel_time(M, 0.0);
        for (int i = 0; i < M; i++) {
            double ratio = (edges[i].capacity > 0.0) ? (flow[i] / edges[i].capacity) : 0.0;
            travel_time[i] = edges[i].base_time * (1.0 + congestion_factor * std::pow(ratio, exponent));
        }
        
        // Solve shortest path for each trip to build auxiliary flow f_aux
        std::vector<double> f_aux(M, 0.0);
        for (const auto &trip : trips) {
            std::vector<double> dist(N, std::numeric_limits<double>::infinity());
            std::vector<int> prev_edge(N, -1);
            std::priority_queue<NodeState, std::vector<NodeState>, std::greater<NodeState>> pq;
            
            dist[trip.source] = 0.0;
            pq.push({0.0, trip.source});
            
            while (!pq.empty()) {
                NodeState cur = pq.top();
                pq.pop();
                int u = cur.node;
                if (cur.dist > dist[u]) continue;
                if(u == trip.dest) break;
                for (int e_idx : graph[u]) {
                    int v = edges[e_idx].v;
                    double new_dist = dist[u] + travel_time[e_idx];
                    if(new_dist < dist[v]) {
                        dist[v] = new_dist;
                        prev_edge[v] = e_idx;
                        pq.push({new_dist, v});
                    }
                }
            }
            // If destination unreachable, skip this trip
            if (dist[trip.dest] == std::numeric_limits<double>::infinity()) {
                continue;
            }
            // Reconstruct the path and add the trip's demand to each edge in the path
            int cur_node = trip.dest;
            std::vector<int> path_edges;
            while (cur_node != trip.source) {
                int e_idx = prev_edge[cur_node];
                path_edges.push_back(e_idx);
                cur_node = edges[e_idx].u;
            }
            // Reverse the path to get correct order (from source to dest)
            for (int e : path_edges) {
                // In the auxiliary solution, we assign full demand along the chosen path.
                f_aux[e] += trip.demand;
            }
        }
        
        // Compute step size (using diminishing step length rule)
        double alpha = 1.0 / (iter + 1);
        
        // Update flows: new_flow = old_flow + alpha*(f_aux - old_flow)
        double max_change = 0.0;
        for (int i = 0; i < M; i++) {
            double new_flow = flow[i] + alpha * (f_aux[i] - flow[i]);
            // Enforce capacity constraints: if new_flow exceeds capacity, clamp to capacity.
            if(new_flow > edges[i].capacity) {
                new_flow = edges[i].capacity;
            }
            double change = std::abs(new_flow - flow[i]);
            if(change > max_change)
                max_change = change;
            flow[i] = new_flow;
        }
        
        if (max_change < tolerance)
            break;
    }
    
    // Output flows for each road in the input order
    out << std::fixed << std::setprecision(2);
    for (int i = 0; i < M; i++) {
        out << flow[i] << "\n";
    }
}

} // end namespace traffic_router