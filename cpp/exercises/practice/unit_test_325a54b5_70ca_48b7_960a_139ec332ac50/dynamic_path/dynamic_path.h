#pragma once

#include <vector>

class DynamicPath {
public:
    DynamicPath(int n, const std::vector<std::vector<int>>& edges);
    
    // Find the shortest path from node start to node end
    long long findShortestPath(int start, int end);
    
    // Update the cost of edge between nodes u and v
    void updateEdge(int u, int v, int newCost);
};