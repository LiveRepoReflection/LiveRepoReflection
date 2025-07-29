#include "drone_delivery.h"
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

namespace drone_delivery {

DroneDeliverySystem::DroneDeliverySystem(const std::vector<int>& intersections, const std::vector<Street>& streets) {
    int max_id = 0;
    for (int node : intersections) {
        if (node > max_id) {
            max_id = node;
        }
    }
    adj.resize(max_id + 1);
    nodes = intersections;
    for (const auto& s : streets) {
        if (s.from >= 0 && s.from < static_cast<int>(adj.size()) && s.to >= 0 && s.to < static_cast<int>(adj.size())) {
            adj[s.from].push_back(s);
        }
    }
}

std::vector<int> DroneDeliverySystem::plan_route(const DeliveryRequest& request) {
    int n = static_cast<int>(adj.size());
    std::vector<int> dist(n, std::numeric_limits<int>::max());
    std::vector<int> prev(n, -1);
    using pii = std::pair<int, int>;
    std::priority_queue<pii, std::vector<pii>, std::greater<pii>> pq;

    if (request.start_intersection < 0 || request.start_intersection >= n ||
        request.destination_intersection < 0 || request.destination_intersection >= n) {
        return std::vector<int>();
    }
    
    dist[request.start_intersection] = 0;
    pq.push({0, request.start_intersection});
    
    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();
        if (d > dist[u]) continue;
        if (u == request.destination_intersection) break;
        for (auto& edge : adj[u]) {
            if (edge.capacity < 1) continue;
            int v = edge.to;
            int nd = d + edge.travel_time;
            if (nd < dist[v]) {
                dist[v] = nd;
                prev[v] = u;
                pq.push({nd, v});
            }
        }
    }
    
    if (dist[request.destination_intersection] == std::numeric_limits<int>::max() ||
        dist[request.destination_intersection] > request.deadline) {
        return std::vector<int>();
    }
    
    std::vector<int> route;
    for (int at = request.destination_intersection; at != -1; at = prev[at]) {
        route.push_back(at);
    }
    std::reverse(route.begin(), route.end());
    return route;
}

} // namespace drone_delivery