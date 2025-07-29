#include "network_reliability.h"

#include <vector>
#include <tuple>
#include <sstream>
#include <string>
#include <algorithm>
#include <iomanip>
#include <unordered_map>
#include <numeric>

namespace network_reliability {

struct Edge {
    int u;
    int v;
    double p;
};

bool operator<(const Edge& a, const Edge& b) {
    if (a.u != b.u) return a.u < b.u;
    if (a.v != b.v) return a.v < b.v;
    return a.p < b.p;
}

bool operator==(const Edge& a, const Edge& b) {
    return a.u == b.u && a.v == b.v && std::abs(a.p - b.p) < 1e-9;
}

// Union-Find for connectivity checks.
struct UnionFind {
    std::vector<int> parent;
    UnionFind(int n) : parent(n) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    int find(int x) {
        return parent[x] == x ? x : parent[x] = find(parent[x]);
    }
    void unionn(int a, int b) {
        a = find(a);
        b = find(b);
        if (a != b)
            parent[b] = a;
    }
};

// Check if the graph represented by n nodes and edges is connected.
bool isConnected(int n, const std::vector<Edge>& edges) {
    if (n == 0) return true;
    UnionFind uf(n);
    for (const auto& edge : edges) {
        uf.unionn(edge.u, edge.v);
    }
    int rep = uf.find(0);
    for (int i = 1; i < n; i++) {
        if (uf.find(i) != rep)
            return false;
    }
    return true;
}

// Generate a canonical key for a given state (n and sorted edges).
std::string stateKey(int n, const std::vector<Edge>& edges) {
    std::ostringstream oss;
    oss << n << ":";
    for (const auto& edge : edges) {
        oss << edge.u << "," << edge.v << ",";
        oss << std::fixed << std::setprecision(6) << edge.p << ";";
    }
    return oss.str();
}

// Remove one occurrence of edge e from edges.
std::vector<Edge> removeEdge(const std::vector<Edge>& edges, const Edge& e) {
    std::vector<Edge> newEdges;
    bool removed = false;
    for (const auto& edge : edges) {
        if (!removed && edge == e) {
            removed = true;
            continue;
        }
        newEdges.push_back(edge);
    }
    std::sort(newEdges.begin(), newEdges.end());
    return newEdges;
}

// Contract the given edge in the graph.
// Uses the rule: Let a = min(u,v) and b = max(u,v). Merge b into a,
// and then renumber nodes > b by subtracting one.
std::pair<int, std::vector<Edge>> contractEdge(int n, const std::vector<Edge>& edges, const Edge& e) {
    int a = std::min(e.u, e.v);
    int b = std::max(e.u, e.v);
    int new_n = n - 1;
    std::vector<Edge> newEdges;
    bool skipped = false; // to remove one occurrence of the contracted edge.
    for (const auto& edge : edges) {
        // Skip exactly one occurrence of the edge we are contracting.
        if (!skipped && edge == e) {
            skipped = true;
            continue;
        }
        // Update endpoints.
        int nu = edge.u;
        int nv = edge.v;
        // Replace b with a.
        if (nu == b) nu = a;
        if (nv == b) nv = a;
        // Adjust numbering for vertices greater than b.
        if (nu > b) nu--;
        if (nv > b) nv--;
        // Remove self-loops.
        if (nu == nv) continue;
        Edge newEdge;
        newEdge.u = std::min(nu, nv);
        newEdge.v = std::max(nu, nv);
        newEdge.p = edge.p;
        newEdges.push_back(newEdge);
    }
    std::sort(newEdges.begin(), newEdges.end());
    return { new_n, newEdges };
}

// Check if a specific edge is a bridge in the current state.
bool isBridge(int n, const std::vector<Edge>& edges, const Edge& e) {
    std::vector<Edge> edgesWithout = removeEdge(edges, e);
    return !isConnected(n, edgesWithout);
}

// Memoization cache.
std::unordered_map<std::string, double> memo;

double reliabilityUtil(int n, const std::vector<Edge>& edges) {
    // If the graph (with all edges assumed available) is not connected, return 0.
    if (!isConnected(n, edges))
        return 0.0;
    if (n == 1) 
        return 1.0;
    // If there are no edges and multiple nodes, the graph is disconnected.
    if (edges.empty())
        return 0.0;

    std::string key = stateKey(n, edges);
    if (memo.find(key) != memo.end())
        return memo[key];

    // Pick the first edge.
    Edge e = edges[0];

    // Compute removal (deletion) branch.
    std::vector<Edge> edges_without = removeEdge(edges, e);
    double prob = 0.0;
    if (isBridge(n, edges, e)) {
        // e is a bridge: if it fails, connectivity is lost.
        auto contracted = contractEdge(n, edges, e);
        prob = e.p * reliabilityUtil(contracted.first, contracted.second);
    } else {
        auto contracted = contractEdge(n, edges, e);
        double withEdge = reliabilityUtil(contracted.first, contracted.second);
        double withoutEdge = reliabilityUtil(n, edges_without);
        prob = e.p * withEdge + (1.0 - e.p) * withoutEdge;
    }
    memo[key] = prob;
    return prob;
}

double compute_network_reliability(int n, const std::vector<std::tuple<int, int, double>>& inputEdges) {
    std::vector<Edge> edges;
    // Transform input tuples to Edge structure.
    for (const auto& tup : inputEdges) {
        int u, v;
        double p;
        std::tie(u, v, p) = tup;
        Edge e;
        e.u = std::min(u, v);
        e.v = std::max(u, v);
        e.p = p;
        edges.push_back(e);
    }
    std::sort(edges.begin(), edges.end());
    memo.clear();
    return reliabilityUtil(n, edges);
}

}  // namespace network_reliability