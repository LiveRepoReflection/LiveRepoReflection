#include "network_optimize.h"
#include <vector>
#include <tuple>
#include <algorithm>
#include <limits>

namespace network_optimize {

    struct Edge {
        int u;
        int v;
        long long cost;
        Edge(int _u, int _v, long long _cost) : u(_u), v(_v), cost(_cost) {}
    };

    struct UnionFind {
        std::vector<int> parent;
        std::vector<int> rank;
        UnionFind(int n) : parent(n), rank(n, 0) {
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }

        int find(int x) {
            if (parent[x] != x)
                parent[x] = find(parent[x]);
            return parent[x];
        }

        bool unite(int x, int y) {
            int rx = find(x), ry = find(y);
            if (rx == ry) return false;
            if (rank[rx] < rank[ry]) {
                parent[rx] = ry;
            } else if (rank[rx] > rank[ry]) {
                parent[ry] = rx;
            } else {
                parent[ry] = rx;
                rank[rx]++;
            }
            return true;
        }
    };

    long long compute_minimum_cost(int n, const std::vector<int>& b, 
                                   const std::vector<std::tuple<int, int, long long>>& roads) {
        // Build edge list. Only include roads that exist (given in the input).
        // The cost of an edge is defined as: max(b[u], b[v]) * w.
        std::vector<Edge> edges;
        for (const auto& road : roads) {
            int u, v;
            long long w;
            std::tie(u, v, w) = road;
            long long edgeCost = static_cast<long long>(std::max(b[u], b[v])) * w;
            edges.emplace_back(u, v, edgeCost);
        }
        
        // Sort edges based on cost (ascending order)
        std::sort(edges.begin(), edges.end(), [](const Edge& e1, const Edge& e2) {
            return e1.cost < e2.cost;
        });
        
        UnionFind uf(n);
        long long totalCost = 0;
        int edgesUsed = 0;
        for (const auto& edge : edges) {
            if (uf.unite(edge.u, edge.v)) {
                totalCost += edge.cost;
                edgesUsed++;
                if (edgesUsed == n - 1) break;
            }
        }
        
        // Check if all cities are connected
        if (edgesUsed != n - 1) return -1;
        return totalCost;
    }
}