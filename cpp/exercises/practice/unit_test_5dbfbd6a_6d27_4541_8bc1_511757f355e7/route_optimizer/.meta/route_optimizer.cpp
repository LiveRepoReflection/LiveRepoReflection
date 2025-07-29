#include "route_optimizer.h"
#include <queue>
#include <unordered_map>
#include <limits>
#include <set>

namespace route_optimizer {

struct State {
    int location;
    std::string current_mode;
    double cost;

    State(int loc, const std::string& mode, double c) 
        : location(loc), current_mode(mode), cost(c) {}

    bool operator>(const State& other) const {
        return cost > other.cost;
    }
};

double find_minimum_time(
    const std::vector<int>& locations,
    const std::vector<std::tuple<int, int, std::string, double, double>>& edges,
    const std::vector<std::tuple<int, std::string, std::string, double>>& transfers,
    int start,
    int destination) {

    if (start == destination) return 0.0;

    // Build adjacency list
    std::unordered_map<int, std::vector<std::tuple<int, std::string, double>>> adj;
    for (const auto& edge : edges) {
        int src = std::get<0>(edge);
        int dst = std::get<1>(edge);
        std::string mode = std::get<2>(edge);
        double distance = std::get<3>(edge);
        double cost_per_unit = std::get<4>(edge);
        adj[src].emplace_back(dst, mode, distance * cost_per_unit);
    }

    // Build transfer map
    std::unordered_map<int, std::vector<std::tuple<std::string, std::string, double>>> transfer_map;
    for (const auto& transfer : transfers) {
        int location = std::get<0>(transfer);
        std::string from_mode = std::get<1>(transfer);
        std::string to_mode = std::get<2>(transfer);
        double transfer_time = std::get<3>(transfer);
        transfer_map[location].emplace_back(from_mode, to_mode, transfer_time);
    }

    // Distance map stores the minimum cost to reach a location using a specific mode
    std::unordered_map<int, std::unordered_map<std::string, double>> dist;
    for (int loc : locations) {
        dist[loc] = std::unordered_map<std::string, double>();
    }

    // Priority queue for Dijkstra's algorithm
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;

    // Initialize with all possible modes at start location
    std::set<std::string> initial_modes;
    for (const auto& edge : edges) {
        if (std::get<0>(edge) == start) {
            initial_modes.insert(std::get<2>(edge));
        }
    }

    for (const auto& mode : initial_modes) {
        pq.push(State(start, mode, 0.0));
        dist[start][mode] = 0.0;
    }

    while (!pq.empty()) {
        State current = pq.top();
        pq.pop();

        // Skip if we've found a better path
        if (dist[current.location].count(current.current_mode) && 
            dist[current.location][current.current_mode] < current.cost) {
            continue;
        }

        // Try all direct connections
        for (const auto& [next_loc, mode, edge_cost] : adj[current.location]) {
            if (mode == current.current_mode) {
                double new_cost = current.cost + edge_cost;
                if (!dist[next_loc].count(mode) || new_cost < dist[next_loc][mode]) {
                    dist[next_loc][mode] = new_cost;
                    pq.push(State(next_loc, mode, new_cost));
                }
            }
        }

        // Try all possible transfers at current location
        if (transfer_map.count(current.location)) {
            for (const auto& [from_mode, to_mode, transfer_cost] : transfer_map[current.location]) {
                if (from_mode == current.current_mode) {
                    double new_cost = current.cost + transfer_cost;
                    if (!dist[current.location].count(to_mode) || 
                        new_cost < dist[current.location][to_mode]) {
                        dist[current.location][to_mode] = new_cost;
                        pq.push(State(current.location, to_mode, new_cost));
                    }
                }
            }
        }
    }

    // Find minimum cost to reach destination using any mode
    double min_cost = std::numeric_limits<double>::infinity();
    for (const auto& [mode, cost] : dist[destination]) {
        min_cost = std::min(min_cost, cost);
    }

    return min_cost == std::numeric_limits<double>::infinity() ? -1.0 : min_cost;
}

}