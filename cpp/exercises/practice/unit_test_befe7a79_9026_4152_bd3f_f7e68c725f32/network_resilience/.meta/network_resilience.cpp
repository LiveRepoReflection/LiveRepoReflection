#include "network_resilience.h"
#include <vector>
#include <tuple>
#include <climits>

using namespace std;

namespace network_resilience {

struct UnionFind {
    vector<int> parent;
    vector<int> rank;
    UnionFind(int n) : parent(n), rank(n, 0) {
        for (int i = 0; i < n; i++) {
            parent[i] = i;
        }
    }
    int find(int a) {
        if (parent[a] != a) {
            parent[a] = find(parent[a]);
        }
        return parent[a];
    }
    void unionSet(int a, int b) {
        int rootA = find(a);
        int rootB = find(b);
        if (rootA == rootB) return;
        if (rank[rootA] < rank[rootB]) {
            parent[rootA] = rootB;
        } else if (rank[rootA] > rank[rootB]) {
            parent[rootB] = rootA;
        } else {
            parent[rootB] = rootA;
            rank[rootA]++;
        }
    }
};

int maximum_resilience(int N, const vector<tuple<int, int, int>> &edges) {
    // Initialize Union-Find structure for N nodes.
    UnionFind uf(N);
    
    // Union nodes connected by an edge.
    for (const auto &edge : edges) {
        int u, v, cost;
        tie(u, v, cost) = edge;
        uf.unionSet(u, v);
    }
    
    // For each component, find the minimum edge cost.
    // We use a vector of size N, where each index represents a potential component leader.
    vector<int> component_min(N, INT_MAX);
    for (const auto &edge : edges) {
        int u, v, cost;
        tie(u, v, cost) = edge;
        int root = uf.find(u);
        if (cost < component_min[root]) {
            component_min[root] = cost;
        }
    }
    
    // The overall resilience is the minimum of the finite component edge costs.
    // Components with no edges are considered to have infinite resilience (represented by INT_MAX).
    int overall = INT_MAX;
    for (int i = 0; i < N; i++) {
        // Check only the components leaders.
        if (uf.find(i) == i) {
            if (component_min[i] != INT_MAX && component_min[i] < overall) {
                overall = component_min[i];
            }
        }
    }
    
    return overall;
}

}