#include "delivery_network.h"
#include <vector>
#include <tuple>
#include <algorithm>

namespace delivery_network {

struct Edge {
    int u, v;
    double cost;
    Edge(int u, int v, double cost) : u(u), v(v), cost(cost) {}
};

struct UnionFind {
    std::vector<int> parent;
    UnionFind(int n) : parent(n) {
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
    
    bool unite(int x, int y) {
        int rootX = find(x);
        int rootY = find(y);
        if (rootX == rootY) {
            return false;
        }
        parent[rootY] = rootX;
        return true;
    }
};

double computeOptimalCost(int num_cities, const std::vector<std::tuple<int, int, int, int>>& roads, double distance_weight, double toll_weight) {
    std::vector<Edge> edges;
    edges.reserve(roads.size());
    for (const auto& road : roads) {
        int u, v, distance, toll;
        std::tie(u, v, distance, toll) = road;
        double cost = distance * distance_weight + toll * toll_weight;
        edges.push_back(Edge(u, v, cost));
    }
    
    std::sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {
        return a.cost < b.cost;
    });
    
    UnionFind uf(num_cities);
    double totalCost = 0.0;
    for (const auto& edge : edges) {
        if (uf.unite(edge.u, edge.v)) {
            totalCost += edge.cost;
        }
    }
    return totalCost;
}

} // namespace delivery_network