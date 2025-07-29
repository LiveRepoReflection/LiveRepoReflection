#include "traffic_tolls.h"
#include <vector>
#include <queue>
#include <limits>
#include <cmath>

using namespace std;

struct Node {
    int vertex;
    double dist;
    // For reconstructing the path: pre and edge index used
    int prev;
    int edgeIndex;
    bool operator>(const Node& other) const { return dist > other.dist; }
};

// Helper function: Dijkstra on the graph constructed from edges.
// Each edge weight is calculated based on zero toll use: 
// travel_time = base_travel_time * (1 + (initial_vehicles/capacity)^2)
bool dijkstra(const vector<vector<pair<int, pair<double, int>>>> &adj, int source, int destination, vector<int>& parent, vector<int>& parentEdge) {
    int n = adj.size();
    vector<double> dist(n, numeric_limits<double>::max());
    priority_queue<Node, vector<Node>, greater<Node>>pq;
    
    dist[source] = 0;
    parent[source] = -1;
    parentEdge[source] = -1;
    pq.push({source, 0, -1, -1});
    
    while(!pq.empty()){
        Node cur = pq.top();
        pq.pop();
        if(cur.dist > dist[cur.vertex]) continue;
        if(cur.vertex == destination) break;
        for(auto &ne : adj[cur.vertex]){
            int next = ne.first;
            double weight = ne.second.first;
            int edgeIdx = ne.second.second;
            if(dist[cur.vertex] + weight < dist[next]){
                dist[next] = dist[cur.vertex] + weight;
                parent[next] = cur.vertex;
                parentEdge[next] = edgeIdx;
                pq.push({next, dist[next], cur.vertex, edgeIdx});
            }
        }
    }
    return (dist[destination] < numeric_limits<double>::max());
}

// Binary search to solve for toll value T that satisfies:
// f(T) = T * v * exp(-s * T) = target
double computeToll(double v, double s, double target) {
    double T_low = 0.0;
    double T_high = 1.0 / s; // maximum occurs at T = 1/s
    // maximum revenue possible from this edge:
    double f_max = (1.0/s) * v * exp(-1.0);
    if (target >= f_max) {
        return T_high; // assign maximum toll value we can apply
    }
    
    // Binary search tolerance:
    double tol = 1e-7;
    double mid;
    for (int iter = 0; iter < 100; iter++) {
        mid = (T_low + T_high) / 2.0;
        double f_mid = mid * v * exp(-s * mid);
        if (fabs(f_mid - target) < tol) {
            break;
        }
        if (f_mid < target) {
            T_low = mid;
        } else {
            T_high = mid;
        }
    }
    return mid;
}

std::vector<double> optimizeTolls(const std::vector<Edge>& edges, double tollSensitivity, double budget, int source, int destination) {
    // Special case: insufficient budget implies no meaningful effect.
    if (budget <= 0) {
        return std::vector<double>{-1};
    }
    
    // Determine number of nodes.
    int maxNode = 0;
    for (const auto &e : edges) {
        if (e.source > maxNode)
            maxNode = e.source;
        if (e.destination > maxNode)
            maxNode = e.destination;
    }
    int n = maxNode + 1;
    
    // Build the adjacency list using base travel times at zero toll.
    // travel_time = base_travel_time * (1 + (initial_vehicles/capacity)^2)
    vector<vector<pair<int, pair<double, int>>>> adj(n);
    for (size_t i = 0; i < edges.size(); i++) {
        const Edge &e = edges[i];
        double congestionFactor = static_cast<double>(e.initial_vehicles) / e.capacity;
        double travelTime = e.base_travel_time * (1.0 + congestionFactor * congestionFactor);
        adj[e.source].push_back({e.destination, {travelTime, static_cast<int>(i)}});
    }
    
    // Run Dijkstra to check if there's a valid path from source to destination.
    vector<int> parent(n, -1);
    vector<int> parentEdge(n, -1);
    bool pathExists = dijkstra(adj, source, destination, parent, parentEdge);
    if (!pathExists) {
        // Return error vector: size equal to edges, filled with -1.
        return std::vector<double>(edges.size(), -1);
    }
    
    // Reconstruct the shortest path edge indices.
    vector<int> pathEdges;
    int cur = destination;
    while (parent[cur] != -1) {
        pathEdges.push_back(parentEdge[cur]);
        cur = parent[cur];
    }
    
    // Reverse to get path in order from source to destination.
    std::reverse(pathEdges.begin(), pathEdges.end());
    int k = pathEdges.size();
    // If path is empty, then something is wrong.
    if (k == 0) {
        return std::vector<double>(edges.size(), -1);
    }
    
    // Distribute budget equally among the edges on the path.
    double targetRevenuePerEdge = budget / k;
    
    // Prepare results vector: For each edge, assign toll.
    vector<double> tolls(edges.size(), 0.0);
    
    // For each edge in the chosen path, compute optimal toll.
    for (int idx : pathEdges) {
        const Edge &e = edges[idx];
        double v = e.initial_vehicles;
        // Compute maximum possible revenue for this edge:
        double T_max = 1.0 / tollSensitivity;
        double f_max = T_max * v * exp(-tollSensitivity * T_max);
        
        double tollValue = 0.0;
        if (targetRevenuePerEdge >= f_max) {
            tollValue = T_max;
        } else {
            tollValue = computeToll(v, tollSensitivity, targetRevenuePerEdge);
        }
        tolls[idx] = tollValue;
    }
    // For edges not on the chosen path, toll remains 0.
    
    return tolls;
}