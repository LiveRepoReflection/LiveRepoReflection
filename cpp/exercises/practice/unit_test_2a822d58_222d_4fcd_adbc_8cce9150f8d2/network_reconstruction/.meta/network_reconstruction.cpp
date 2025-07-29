#include "network_reconstruction.h"
#include <vector>
#include <limits>
#include <cstdlib>

using namespace std;

namespace network_reconstruction {

// Union-Find data structure for grouping nodes
class UnionFind {
public:
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
    void union_set(int x, int y) {
        int xroot = find(x);
        int yroot = find(y);
        if (xroot == yroot) return;
        if (rank[xroot] < rank[yroot]) {
            parent[xroot] = yroot;
        } else if (rank[xroot] > rank[yroot]) {
            parent[yroot] = xroot;
        } else {
            parent[yroot] = xroot;
            rank[xroot]++;
        }
    }
private:
    vector<int> parent;
    vector<int> rank;
};

// Function to run Prim's MST over a given component of nodes.
// compNodes: vector of node ids in the component.
// cost: global cost matrix.
vector<pair<int,int>> primMST(const vector<int>& compNodes, const vector<vector<int>>& cost) {
    vector<pair<int,int>> mstEdges;
    if (compNodes.empty() || compNodes.size() == 1)
        return mstEdges;

    int compSize = compNodes.size();
    const int INF = numeric_limits<int>::max();
    // inMST[node] indicates whether the node (by global id) is included in MST.
    vector<bool> inMST(10000, false);  // sufficiently large; N is passed in reconstruct_network.
    // Minimal cost edge for each node not yet in MST.
    vector<int> minCost(10000, INF);
    // Stores closest node in MST for a given node (global id), will form edge (closest, node)
    vector<int> parent(10000, -1);

    // Initialize start node, choose first in compNodes.
    int start = compNodes[0];
    inMST[start] = true;
    
    // For each other node in component, set cost from start
    for (int i = 0; i < compSize; i++) {
        int node = compNodes[i];
        if (node != start) {
            minCost[node] = cost[start][node];
            parent[node] = start;
        }
    }
    
    // We need to add compSize - 1 edges.
    for (int i = 1; i < compSize; i++) {
        int bestCost = INF;
        int bestNode = -1;
        
        // Select the node in component not in MST with smallest cost edge.
        for (int node : compNodes) {
            if (!inMST[node] && minCost[node] < bestCost) {
                bestCost = minCost[node];
                bestNode = node;
            }
        }
        if (bestNode == -1) {
            break; // Should not happen if graph is connected.
        }
        // Include bestNode in MST.
        inMST[bestNode] = true;
        mstEdges.push_back({parent[bestNode], bestNode});
        
        // Update adjacent nodes cost from the newly added node.
        for (int node : compNodes) {
            if (!inMST[node] && cost[bestNode][node] < minCost[node]) {
                minCost[node] = cost[bestNode][node];
                parent[node] = bestNode;
            }
        }
    }
    
    return mstEdges;
}

// Main function to reconstruct the network
// The strategy is to group nodes that need connectivity based on flows (ignoring self-flows).
// For each group (component), we build a minimum spanning tree using Prim's algorithm over the complete graph defined by the cost matrix.
vector<pair<int,int>> reconstruct_network(int N, const vector<FlowRecord>& flows, const vector<vector<int>>& cost) {
    vector<pair<int,int>> result;
    // If no flows exist, return empty network.
    if (flows.empty())
        return result;
    
    UnionFind uf(N);
    // Track which nodes are involved in flows.
    vector<bool> involved(N, false);
    
    // Process each flow record
    for (const auto &flow : flows) {
        // Skip self-flows
        if (flow.source == flow.destination)
            continue;
        involved[flow.source] = true;
        involved[flow.destination] = true;
        uf.union_set(flow.source, flow.destination);
    }
    
    // Map from component representative to nodes in that component.
    vector<vector<int>> components(N);
    for (int i = 0; i < N; i++) {
        if (involved[i]) {
            int root = uf.find(i);
            components[root].push_back(i);
        }
    }
    
    // For each component compute the MST and add its edges.
    for (int i = 0; i < N; i++) {
        if (!components[i].empty()) {
            vector<pair<int,int>> compMST = primMST(components[i], cost);
            // Append MST edges to result
            for (auto &edge : compMST) {
                result.push_back(edge);
            }
        }
    }
    
    return result;
}

}  // namespace network_reconstruction