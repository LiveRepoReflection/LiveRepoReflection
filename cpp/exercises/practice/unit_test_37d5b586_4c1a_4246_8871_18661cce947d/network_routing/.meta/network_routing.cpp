#include "network_routing.h"
#include <vector>
#include <tuple>
#include <algorithm>

namespace network_routing {

struct UnionFind {
    std::vector<int> parent;
    std::vector<int> rank;
    
    UnionFind(int n) : parent(n), rank(n, 0) {
        for (int i = 0; i < n; ++i) {
            parent[i] = i;
        }
    }
    
    int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);
        }
        return parent[x];
    }
    
    void unite(int a, int b) {
        a = find(a);
        b = find(b);
        if (a == b) return;
        if (rank[a] < rank[b]) {
            parent[a] = b;
        } else if (rank[a] > rank[b]) {
            parent[b] = a;
        } else {
            parent[b] = a;
            rank[a]++;
        }
    }
};

int find_optimal_latency(int N, const std::vector<std::tuple<int, int, int>> &edges, int src, int dest) {
    if (src == dest) {
        return 0;
    }
    // Make a copy of the edges and sort them by latency in ascending order.
    std::vector<std::tuple<int, int, int>> sortedEdges(edges);
    std::sort(sortedEdges.begin(), sortedEdges.end(), [](const std::tuple<int, int, int> &a, const std::tuple<int, int, int> &b) {
        return std::get<2>(a) < std::get<2>(b);
    });
    
    // Utilize union-find (disjoint set) to connect nodes gradually.
    UnionFind uf(N);
    for (const auto &edge : sortedEdges) {
        int u, v, latency;
        u = std::get<0>(edge);
        v = std::get<1>(edge);
        latency = std::get<2>(edge);
        uf.unite(u, v);
        // Check if src and dest are connected.
        if (uf.find(src) == uf.find(dest)) {
            return latency;
        }
    }
    return -1;
}

}