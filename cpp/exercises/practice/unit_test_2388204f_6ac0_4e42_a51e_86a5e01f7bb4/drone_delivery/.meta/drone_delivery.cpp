#include "drone_delivery.h"
#include <queue>
#include <vector>
#include <algorithm>
#include <limits>
#include <tuple>
#include <utility>
#include <unordered_map>
#include <unordered_set>

namespace drone_delivery {

// Custom PriorityQueue element for Dijkstra's algorithm
struct PQElement {
    int location;
    int arrival_time;
    
    // Constructor
    PQElement(int loc, int time) : location(loc), arrival_time(time) {}
    
    // Overload operator for priority queue (min heap based on arrival time)
    bool operator>(const PQElement& other) const {
        return arrival_time > other.arrival_time;
    }
};

int find_earliest_arrival_time(
    int N,
    const std::vector<std::tuple<int, int, int>>& edges,
    const std::vector<std::pair<int, int>>& time_windows,
    const std::vector<int>& start_locations,
    int target_location
) {
    // Build adjacency list representation of the graph
    std::vector<std::vector<std::pair<int, int>>> graph(N);
    for (const auto& edge : edges) {
        int u = std::get<0>(edge);
        int v = std::get<1>(edge);
        int w = std::get<2>(edge);
        graph[u].push_back({v, w});
    }
    
    // Priority queue for Dijkstra's algorithm (min heap by arrival time)
    std::priority_queue<PQElement, std::vector<PQElement>, std::greater<PQElement>> pq;
    
    // Distance array to store earliest arrival time at each location
    std::vector<int> earliest_arrival(N, std::numeric_limits<int>::max());
    
    // Initialize the priority queue with start locations
    for (int start : start_locations) {
        if (start == target_location) {
            // If target is a start location, return the start of its time window
            return time_windows[target_location].first;
        }
        
        // Start time is the earliest time in the time window of the start location
        int start_time = time_windows[start].first;
        earliest_arrival[start] = start_time;
        pq.push(PQElement(start, start_time));
    }
    
    // Dijkstra's algorithm
    while (!pq.empty()) {
        PQElement current = pq.top();
        pq.pop();
        
        int location = current.location;
        int arrival_time = current.arrival_time;
        
        // If this is not the earliest known arrival at this location, skip
        if (arrival_time > earliest_arrival[location]) {
            continue;
        }
        
        // If we've reached the target, return the arrival time
        if (location == target_location) {
            return arrival_time;
        }
        
        // Explore neighbors
        for (const auto& neighbor : graph[location]) {
            int next_location = neighbor.first;
            int travel_time = neighbor.second;
            
            // Calculate when we would arrive at the next location
            int next_arrival_time = arrival_time + travel_time;
            
            // Check if we can make it within the time window
            int next_window_start = time_windows[next_location].first;
            int next_window_end = time_windows[next_location].second;
            
            // If we arrive before the window starts, we have to wait
            if (next_arrival_time < next_window_start) {
                next_arrival_time = next_window_start;
            }
            
            // If we arrive after the window ends, we can't deliver here
            if (next_arrival_time > next_window_end) {
                continue;
            }
            
            // If this is a better arrival time than what we've found before, update
            if (next_arrival_time < earliest_arrival[next_location]) {
                earliest_arrival[next_location] = next_arrival_time;
                pq.push(PQElement(next_location, next_arrival_time));
            }
        }
    }
    
    // If we get here, there's no valid path to the target
    return -1;
}

}  // namespace drone_delivery