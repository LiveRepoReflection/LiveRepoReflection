#include "traffic_flow.h"
#include <vector>
#include <tuple>
#include <algorithm>

namespace traffic_flow {

// Depth First Search to find an augmenting path that can push at least req flow from u to sink.
// The function fills the parent vector with the predecessor of each node in the found path.
bool dfs(int u, int sink, std::vector<int>& parent, std::vector<bool>& visited,
         std::vector<std::vector<int>>& res, int req, int n) {
    if (u == sink) return true;
    visited[u] = true;
    for (int v = 0; v < n; v++) {
        if (!visited[v] && res[u][v] >= req) {
            parent[v] = u;
            if (dfs(v, sink, parent, visited, res, req, n))
                return true;
        }
    }
    return false;
}

// Simulate sending flows for two commodities (cars and trucks) with the given targets.
// order = 0 means truck-first then car, order = 1 means car-first then truck.
// For truck augmentation, each unit uses 'k' capacity on every edge in the path,
// and for car augmentation each unit uses 1 capacity.
bool simulateFlow(int order, int carTarget, int truckTarget, int n, int source, int destination,
                  int k, const std::vector<std::vector<int>>& base) {
    std::vector<std::vector<int>> res = base; // residual capacities copy
    int carFlow = 0, truckFlow = 0;
    bool progress = true;
    while (progress && (carFlow < carTarget || truckFlow < truckTarget)) {
        progress = false;
        if (order == 0) { // truck-first then car
            while (truckFlow < truckTarget) {
                std::vector<int> parent(n, -1);
                std::vector<bool> visited(n, false);
                if (!dfs(source, destination, parent, visited, res, k, n))
                    break;
                // Augment truck flow by 1 unit along the found path.
                int v = destination;
                while (v != source) {
                    int u = parent[v];
                    res[u][v] -= k;
                    res[v][u] += k;
                    v = u;
                }
                truckFlow++;
                progress = true;
            }
            while (carFlow < carTarget) {
                std::vector<int> parent(n, -1);
                std::vector<bool> visited(n, false);
                if (!dfs(source, destination, parent, visited, res, 1, n))
                    break;
                // Augment car flow by 1 unit along the found path.
                int v = destination;
                while (v != source) {
                    int u = parent[v];
                    res[u][v] -= 1;
                    res[v][u] += 1;
                    v = u;
                }
                carFlow++;
                progress = true;
            }
        } else { // car-first then truck
            while (carFlow < carTarget) {
                std::vector<int> parent(n, -1);
                std::vector<bool> visited(n, false);
                if (!dfs(source, destination, parent, visited, res, 1, n))
                    break;
                int v = destination;
                while (v != source) {
                    int u = parent[v];
                    res[u][v] -= 1;
                    res[v][u] += 1;
                    v = u;
                }
                carFlow++;
                progress = true;
            }
            while (truckFlow < truckTarget) {
                std::vector<int> parent(n, -1);
                std::vector<bool> visited(n, false);
                if (!dfs(source, destination, parent, visited, res, k, n))
                    break;
                int v = destination;
                while (v != source) {
                    int u = parent[v];
                    res[u][v] -= k;
                    res[v][u] += k;
                    v = u;
                }
                truckFlow++;
                progress = true;
            }
        }
    }
    return (carFlow >= carTarget && truckFlow >= truckTarget);
}

// For a given split: x cars and y trucks (with x + y = total vehicles to send),
// try both augmentation orders to check if the flows can be simultaneously routed.
bool canRouteSplit(int x, int y, int n, int source, int destination, int k,
                   const std::vector<std::vector<int>>& base) {
    // Try truck-first then car
    if (simulateFlow(0, x, y, n, source, destination, k, base))
        return true;
    // Try car-first then truck
    if (simulateFlow(1, x, y, n, source, destination, k, base))
        return true;
    return false;
}

// Check if it is possible to route totalVehicles amount with some split between cars and trucks
// subject to availability: at most numCars cars and at most numTrucks trucks.
bool feasible(int totalVehicles, int numCars, int numTrucks, int n, int source, int destination,
              int k, const std::vector<std::vector<int>>& base) {
    // totalVehicles must be split as x cars and (totalVehicles - x) trucks.
    // x must be in [max(0, totalVehicles - numTrucks), min(totalVehicles, numCars)]
    int low = std::max(0, totalVehicles - numTrucks);
    int high = std::min(totalVehicles, numCars);
    for (int x = low; x <= high; x++) {
        int y = totalVehicles - x;
        if (canRouteSplit(x, y, n, source, destination, k, base))
            return true;
    }
    return false;
}

int maxVehicles(int n, int source, int destination, int k, int numCars, int numTrucks,
                const std::vector<std::tuple<int, int, int>>& edges) {
    // Build the base residual capacity matrix.
    std::vector<std::vector<int>> base(n, std::vector<int>(n, 0));
    for (const auto& edge : edges) {
        int u, v, cap;
        std::tie(u, v, cap) = edge;
        base[u][v] += cap;
    }
    
    int low = 0;
    int high = numCars + numTrucks;
    // Binary search for the maximum total vehicles that can be routed.
    while (low < high) {
        int mid = (low + high + 1) / 2;
        if (feasible(mid, numCars, numTrucks, n, source, destination, k, base))
            low = mid;
        else
            high = mid - 1;
    }
    return low;
}

}  // namespace traffic_flow