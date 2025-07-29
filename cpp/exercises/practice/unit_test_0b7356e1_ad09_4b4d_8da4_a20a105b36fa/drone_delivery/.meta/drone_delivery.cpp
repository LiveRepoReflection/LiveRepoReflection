#include "drone_delivery.h"
#include <vector>
#include <queue>
#include <limits>

using namespace std;

const int INF = numeric_limits<int>::max();

std::vector<int> schedule_deliveries(
    int num_nodes,
    const std::vector<std::vector<std::pair<int, int>>>& adjacency_list,
    const std::vector<std::vector<int>>& delivery_requests,
    int drone_capacity,
    int drone_flight_time
) {
    // Compute the shortest distance from the depot (node 0) to all other nodes using Dijkstra's algorithm.
    vector<int> dist(num_nodes, INF);
    dist[0] = 0;
    typedef pair<int, int> pii; // (distance, node)
    priority_queue<pii, vector<pii>, greater<pii>> pq;
    pq.push({0, 0});
    
    while (!pq.empty()) {
        pii current = pq.top();
        pq.pop();
        int current_dist = current.first;
        int node = current.second;
        if (current_dist > dist[node])
            continue;
        for (const auto& edge : adjacency_list[node]) {
            int neighbor = edge.first;
            int travel_time = edge.second;
            if (current_dist + travel_time < dist[neighbor]) {
                dist[neighbor] = current_dist + travel_time;
                pq.push({dist[neighbor], neighbor});
            }
        }
    }
    
    // Evaluate each delivery request.
    // Each delivery request is specified as:
    // {delivery_id, destination_node, package_weight, delivery_deadline}
    std::vector<int> result;
    for (const auto& request : delivery_requests) {
        if (request.size() != 4)
            continue; // Skip malformed request
        
        int delivery_id = request[0];
        int destination = request[1];
        int package_weight = request[2];
        int deadline = request[3];
        
        // Check package weight constraint.
        if (package_weight > drone_capacity)
            continue;
        
        // Ensure destination is valid and reachable.
        if (destination < 0 || destination >= num_nodes)
            continue;
        if (dist[destination] == INF)
            continue;
        
        int travel_time_to_destination = dist[destination];
        int round_trip_time = travel_time_to_destination * 2;
        
        // Check drone flight time constraint (round-trip must not exceed drone_flight_time).
        if (round_trip_time > drone_flight_time)
            continue;
        
        // Ensure delivery is on-time (arrival at destination on or before deadline).
        if (travel_time_to_destination > deadline)
            continue;
        
        // All criteria met: add the delivery id to the results.
        result.push_back(delivery_id);
    }
    
    return result;
}