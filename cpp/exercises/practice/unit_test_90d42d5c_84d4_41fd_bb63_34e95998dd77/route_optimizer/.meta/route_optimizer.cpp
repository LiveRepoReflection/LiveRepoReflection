#include "route_optimizer.h"
#include <vector>
#include <tuple>
#include <queue>
#include <limits>
#include <algorithm>
#include <cmath>

using namespace std;

namespace route_optimizer {

struct Route {
    int node;
    double time;
    double cost;
    double reliability;
    vector<int> path;
    
    bool operator>(const Route& other) const {
        return cost > other.cost;
    }
};

vector<vector<pair<int, tuple<int, double, double>>>> build_graph(
    const vector<pair<int, int>>& edges,
    const vector<int>& travel_times,
    const vector<double>& toll_costs,
    const vector<double>& reliabilities) {
    
    int max_node = 0;
    for (const auto& edge : edges) {
        max_node = max(max_node, max(edge.first, edge.second));
    }
    
    vector<vector<pair<int, tuple<int, double, double>>>> graph(max_node + 1);
    for (size_t i = 0; i < edges.size(); i++) {
        int u = edges[i].first;
        int v = edges[i].second;
        graph[u].emplace_back(v, make_tuple(travel_times[i], toll_costs[i], reliabilities[i]));
    }
    return graph;
}

tuple<double, double, vector<int>> find_optimal_route(
    const vector<vector<pair<int, tuple<int, double, double>>>>& graph,
    int source,
    int destination,
    double reliability_threshold) {
    
    priority_queue<Route, vector<Route>, greater<Route>> pq;
    vector<double> min_cost(graph.size(), numeric_limits<double>::max());
    vector<double> max_reliability(graph.size(), 0.0);
    
    pq.push({source, 0.0, 0.0, 1.0, {source}});
    min_cost[source] = 0.0;
    max_reliability[source] = 1.0;
    
    while (!pq.empty()) {
        Route current = pq.top();
        pq.pop();
        
        if (current.node == destination) {
            if (current.reliability >= reliability_threshold) {
                return make_tuple(current.time, current.cost, current.path);
            }
            continue;
        }
        
        if (current.cost > min_cost[current.node] && 
            current.reliability < max_reliability[current.node]) {
            continue;
        }
        
        for (const auto& neighbor : graph[current.node]) {
            int v = neighbor.first;
            auto [time, toll, reliability] = neighbor.second;
            
            double new_time = current.time + time;
            double new_cost = current.cost + toll;
            double new_reliability = current.reliability * reliability;
            vector<int> new_path = current.path;
            new_path.push_back(v);
            
            if ((new_cost < min_cost[v] || new_reliability > max_reliability[v]) &&
                new_reliability >= reliability_threshold) {
                if (new_cost < min_cost[v]) {
                    min_cost[v] = new_cost;
                }
                if (new_reliability > max_reliability[v]) {
                    max_reliability[v] = new_reliability;
                }
                pq.push({v, new_time, new_cost, new_reliability, new_path});
            }
        }
    }
    
    return make_tuple(numeric_limits<double>::max(), 
                     numeric_limits<double>::max(), 
                     vector<int>());
}

double calculate_optimal_routes(
    const vector<pair<int, int>>& edges,
    const vector<int>& travel_times,
    const vector<double>& toll_costs,
    const vector<double>& reliabilities,
    const vector<pair<int, double>>& trucks,
    const vector<tuple<int, int, int, int, int>>& deliveries,
    double late_penalty,
    double early_penalty,
    double failure_penalty,
    double reliability_threshold) {
    
    auto graph = build_graph(edges, travel_times, toll_costs, reliabilities);
    double total_cost = 0.0;
    
    for (const auto& delivery : deliveries) {
        auto [source, dest, weight, start_time, end_time] = delivery;
        
        // Find suitable trucks
        vector<size_t> suitable_trucks;
        for (size_t i = 0; i < trucks.size(); i++) {
            if (trucks[i].first >= weight) {
                suitable_trucks.push_back(i);
            }
        }
        
        if (suitable_trucks.empty()) {
            total_cost += failure_penalty;
            continue;
        }
        
        auto [time, route_cost, path] = find_optimal_route(
            graph, source, dest, reliability_threshold);
        
        if (path.empty()) {
            total_cost += failure_penalty;
            continue;
        }
        
        // Find cheapest suitable truck
        double min_truck_cost = numeric_limits<double>::max();
        for (auto truck_idx : suitable_trucks) {
            min_truck_cost = min(min_truck_cost, trucks[truck_idx].second);
        }
        
        double delivery_cost = time * min_truck_cost + route_cost;
        
        // Calculate penalty
        if (time > end_time) {
            delivery_cost += (time - end_time) * late_penalty;
        } else if (time < start_time) {
            delivery_cost += (start_time - time) * early_penalty;
        }
        
        total_cost += delivery_cost;
    }
    
    return total_cost;
}

} // namespace route_optimizer