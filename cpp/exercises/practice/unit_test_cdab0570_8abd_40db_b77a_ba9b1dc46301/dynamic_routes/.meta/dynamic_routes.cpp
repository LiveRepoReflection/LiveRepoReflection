#include "dynamic_routes.h"
#include <queue>
#include <algorithm>
#include <limits>

DynamicRoutes::DynamicRoutes(int n,
                            const std::vector<std::tuple<int, int, int>>& roads,
                            const std::vector<std::tuple<int, int, int, int>>& construction) 
    : n_(n), graph_(n) {
    
    // Build adjacency list
    for (const auto& [from, to, weight] : roads) {
        Edge edge{to, weight, {}};
        graph_[from].push_back(edge);
    }

    // Add construction times
    for (const auto& [from, to, start, end] : construction) {
        for (auto& edge : graph_[from]) {
            if (edge.to == to) {
                edge.blocked_times.emplace_back(start, end);
            }
        }
    }

    // Sort blocked times for each edge
    for (auto& adjacency_list : graph_) {
        for (auto& edge : adjacency_list) {
            std::sort(edge.blocked_times.begin(), edge.blocked_times.end());
        }
    }
}

bool DynamicRoutes::isBlocked(const Edge& edge, int time) {
    for (const auto& [start, end] : edge.blocked_times) {
        if (time >= start && time < end) {
            return true;
        }
    }
    return false;
}

int DynamicRoutes::getNextAvailableTime(const Edge& edge, int current_time) {
    for (const auto& [start, end] : edge.blocked_times) {
        if (current_time >= start && current_time < end) {
            return end;
        }
        if (current_time < start) {
            return current_time;
        }
    }
    return current_time;
}

int DynamicRoutes::findEarliestArrival(int start, int destination, int start_time) {
    const int INF = std::numeric_limits<int>::max();
    std::vector<int> earliest(n_, INF);
    std::priority_queue<std::pair<int, int>, 
                       std::vector<std::pair<int, int>>,
                       std::greater<>> pq;
    
    earliest[start] = start_time;
    pq.push({start_time, start});

    while (!pq.empty()) {
        auto [current_time, current] = pq.top();
        pq.pop();

        if (current_time > earliest[current]) continue;
        if (current == destination) return current_time;

        for (const Edge& edge : graph_[current]) {
            int next_available_time = getNextAvailableTime(edge, current_time);
            int arrival_time = next_available_time + edge.weight;

            if (arrival_time < earliest[edge.to]) {
                earliest[edge.to] = arrival_time;
                pq.push({arrival_time, edge.to});
            }
        }
    }

    return INF;
}

int DynamicRoutes::findOptimalRoute(int start, int destination, int deadline) {
    if (start == destination) return 0;
    
    int result = findEarliestArrival(start, destination, 0);
    
    if (result == std::numeric_limits<int>::max() || result > deadline) {
        return -1;
    }
    
    return result;
}