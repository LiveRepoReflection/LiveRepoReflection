#include "network_partitioning.h"
#include <vector>
#include <utility>
#include <unordered_set>

using std::vector;
using std::pair;
using std::unordered_set;

namespace {

// Union-Find (Disjoint Set Union) Data Structure
struct UnionFind {
    vector<int> parent;
    vector<int> rank;

    UnionFind(int n) : parent(n), rank(n, 0) {
        for (int i = 0; i < n; ++i)
            parent[i] = i;
    }

    int find(int x) {
        if (parent[x] != x)
            parent[x] = find(parent[x]);
        return parent[x];
    }

    void unite(int x, int y) {
        int xp = find(x);
        int yp = find(y);
        if (xp == yp)
            return;
        if (rank[xp] < rank[yp])
            parent[xp] = yp;
        else if (rank[xp] > rank[yp])
            parent[yp] = xp;
        else {
            parent[yp] = xp;
            rank[xp]++;
        }
    }
};

// Hash function for std::pair<int, int>
struct PairHash {
    size_t operator()(const pair<int, int>& p) const {
        return std::hash<long long>()(((long long)p.first) ^ (((long long)p.second) << 32));
    }
};

// Normalize an edge such that the smaller vertex comes first.
pair<int, int> normalize_edge(const pair<int, int>& edge) {
    if (edge.first <= edge.second)
        return edge;
    return {edge.second, edge.first};
}

}  // namespace

namespace network_partitioning {

int min_additional_servers(int N, const vector<pair<int, int>>& edges, const vector<pair<int, int>>& compromised) {
    if (N <= 1)
        return 0;

    // Store compromised edges in a set for O(1) lookup, normalizing each edge.
    unordered_set<pair<int, int>, PairHash> compromised_set;
    for (const auto& edge : compromised) {
        compromised_set.insert(normalize_edge(edge));
    }

    // Use union-find to merge nodes connected by non-compromised edges.
    UnionFind uf(N);
    for (const auto& edge : edges) {
        pair<int, int> norm = normalize_edge(edge);
        if (compromised_set.find(norm) == compromised_set.end()) {
            uf.unite(edge.first, edge.second);
        }
    }

    // Count the number of distinct connected components among the original servers.
    int components = 0;
    vector<bool> seen(N, false);
    for (int i = 0; i < N; ++i) {
        int root = uf.find(i);
        if (!seen[root]) {
            seen[root] = true;
            components++;
        }
    }

    // If the network is already fully connected, no additional server is required.
    if (components <= 1)
        return 0;

    // One added server can serve as a hub connecting one node from each component.
    return 1;
}

}  // namespace network_partitioning