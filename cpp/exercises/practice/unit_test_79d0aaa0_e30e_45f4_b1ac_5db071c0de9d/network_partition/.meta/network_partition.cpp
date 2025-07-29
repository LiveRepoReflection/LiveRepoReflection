#include "network_partition.h"
#include <vector>
#include <tuple>
#include <utility>
#include <algorithm>
#include <numeric>
#include <cmath>

using std::vector;
using std::tuple;
using std::pair;
using std::make_pair;
using std::get;
using std::max;

// Helper function to compute the current objective function value
// given cost sums for partition A and partition B and the capacity cut.
double computeObjective(int costA, int costB, int capacityCut, double lambda) {
    return max(costA, costB) + lambda * capacityCut;
}

vector<int> partitionNetwork(int n, const vector<tuple<int, int, int>>& edges, const vector<int>& costs, double lambda) {
    // Build an adjacency list for quick lookup.
    vector<vector<pair<int, int>>> adj(n);
    for (const auto& edge : edges) {
        int u, v, weight;
        u = get<0>(edge);
        v = get<1>(edge);
        weight = get<2>(edge);
        adj[u].push_back(make_pair(v, weight));
        adj[v].push_back(make_pair(u, weight));
    }

    // Initial partition: assign first n/2 nodes to partition 0 (A), rest to partition 1 (B).
    // Represent partition as an integer vector: 0 indicates Partition A and 1 indicates Partition B.
    vector<int> part(n, 0);
    for (int i = n / 2; i < n; ++i) {
        part[i] = 1;
    }
    
    // Compute initial cost sums for each partition.
    int costA = 0, costB = 0;
    for (int i = 0; i < n; ++i) {
        if (part[i] == 0) {
            costA += costs[i];
        } else {
            costB += costs[i];
        }
    }
    
    // Compute initial capacity cut (each edge counted once).
    int capacityCut = 0;
    for (const auto& edge : edges) {
        int u, v, weight;
        u = get<0>(edge);
        v = get<1>(edge);
        weight = get<2>(edge);
        if (part[u] != part[v]) {
            capacityCut += weight;
        }
    }
    
    double currentObjective = computeObjective(costA, costB, capacityCut, lambda);
    
    // Iterative improvement using node flipping.
    bool improved = true;
    // Limit the maximum iterations to avoid potential infinite loops.
    int maxIterations = 1000;
    int iterations = 0;
    while (improved && iterations < maxIterations) {
        improved = false;
        ++iterations;
        // Try flipping each node and accept flip if it improves the objective.
        for (int i = 0; i < n; ++i) {
            int oldPart = part[i];
            int newPart = 1 - oldPart;
            
            // Cost difference if node i is flipped.
            int newCostA = costA;
            int newCostB = costB;
            if (oldPart == 0) {
                newCostA -= costs[i];
                newCostB += costs[i];
            } else {
                newCostB -= costs[i];
                newCostA += costs[i];
            }
            
            // Compute the change in capacity cut (deltaCut) when flipping node i.
            // For each neighbor j of i:
            // If j is in the same partition as i (oldPart), then edge (i,j) becomes crossing: add weight.
            // If j is in the opposite partition, then edge (i,j) is no longer crossing: subtract weight.
            int deltaCut = 0;
            for (const auto& neighbor : adj[i]) {
                int j = neighbor.first;
                int weight = neighbor.second;
                if (part[j] == oldPart) {
                    // Was not crossing, will become crossing.
                    deltaCut += weight;
                } else {
                    // Was crossing, will not be crossing after flip.
                    deltaCut -= weight;
                }
            }
            
            int newCapacityCut = capacityCut + deltaCut;
            double newObjective = computeObjective(newCostA, newCostB, newCapacityCut, lambda);
            
            if (newObjective < currentObjective) {
                // Accept the flip.
                part[i] = newPart;
                costA = newCostA;
                costB = newCostB;
                capacityCut = newCapacityCut;
                currentObjective = newObjective;
                improved = true;
            }
        }
    }
    
    // Prepare the result: nodes in Partition A.
    vector<int> partitionA;
    for (int i = 0; i < n; ++i) {
        if (part[i] == 0) {
            partitionA.push_back(i);
        }
    }
    
    return partitionA;
}