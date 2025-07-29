#include "optimal_highway.h"
#include <vector>
#include <queue>
#include <algorithm>
#include <limits>
#include <unordered_set>

namespace optimal_highway {

// Union-Find data structure for Kruskal's MST algorithm
class DisjointSet {
private:
    std::vector<int> parent;
    std::vector<int> rank;
    
public:
    DisjointSet(int n) {
        parent.resize(n);
        rank.resize(n);
        for (int i = 0; i < n; ++i) {
            parent[i] = i;
            rank[i] = 0;
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
            return false; // Already in the same set
        }
        
        if (rank[rootX] < rank[rootY]) {
            parent[rootX] = rootY;
        } else {
            parent[rootY] = rootX;
            if (rank[rootX] == rank[rootY]) {
                rank[rootX]++;
            }
        }
        return true;
    }
    
    bool connected(int x, int y) {
        return find(x) == find(y);
    }
    
    int components(int n) {
        std::unordered_set<int> uniqueRoots;
        for (int i = 0; i < n; ++i) {
            uniqueRoots.insert(find(i));
        }
        return uniqueRoots.size();
    }
};

// Implementation of Kruskal's algorithm to find MST
int kruskal(int n, const std::vector<std::tuple<int, int, int, int>>& edges) {
    DisjointSet ds(n);
    int totalCost = 0;
    
    for (const auto& edge : edges) {
        int u = std::get<0>(edge);
        int v = std::get<1>(edge);
        int cost = std::get<2>(edge);
        
        if (ds.unite(u, v)) {
            totalCost += cost;
        }
        
        // If all cities are connected, we're done
        if (ds.components(n) == 1) {
            break;
        }
    }
    
    // Check if all cities are connected
    if (ds.components(n) != 1) {
        return -1; // Not all cities can be connected
    }
    
    return totalCost;
}

// Function to check if all cities can be connected using edges from phases 0 to p
bool canConnectAll(int n, int p, const std::vector<std::vector<std::tuple<int, int, int>>>& phases) {
    DisjointSet ds(n);
    
    // Try to connect cities using edges from phases 0 to p
    for (int i = 0; i <= p; ++i) {
        for (const auto& edge : phases[i]) {
            int u = std::get<0>(edge);
            int v = std::get<1>(edge);
            ds.unite(u, v);
        }
    }
    
    // Check if all cities are connected
    return ds.components(n) == 1;
}

// Main function to find minimum cost
int minimum_cost(int N, int M, const std::vector<std::vector<std::tuple<int, int, int>>>& phases) {
    // Handle single city case
    if (N == 1) {
        return 0;
    }
    
    // Binary search for the earliest phase where connectivity is possible
    int left = 0;
    int right = M - 1;
    int earliestPhase = -1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (canConnectAll(N, mid, phases)) {
            earliestPhase = mid;
            right = mid - 1;
        } else {
            left = mid + 1;
        }
    }
    
    if (earliestPhase == -1) {
        // Not possible to connect all cities
        return -1;
    }
    
    // Collect all edges from phases 0 to earliestPhase
    std::vector<std::tuple<int, int, int, int>> allEdges;
    for (int p = 0; p <= earliestPhase; ++p) {
        for (const auto& edge : phases[p]) {
            int u = std::get<0>(edge);
            int v = std::get<1>(edge);
            int cost = std::get<2>(edge);
            // We add phase number to allow stable sort
            allEdges.push_back(std::make_tuple(u, v, cost, p));
        }
    }
    
    // Sort edges by cost for Kruskal's algorithm
    std::sort(allEdges.begin(), allEdges.end(), 
              [](const auto& a, const auto& b) {
                  return std::get<2>(a) < std::get<2>(b);
              });
    
    // Apply Kruskal's algorithm
    return kruskal(N, allEdges);
}

} // namespace optimal_highway