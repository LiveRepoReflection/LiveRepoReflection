#include "load_balancer.h"
#include <algorithm>
#include <queue>
#include <numeric>
#include <unordered_map>

namespace load_balancer {

// Helper class to model a server with its state
class Server {
public:
    int id;
    int capacity;
    int used_capacity;
    
    Server(int id, int capacity) : id(id), capacity(capacity), used_capacity(0) {}
    
    bool canAcceptRequest() const {
        return used_capacity < capacity;
    }
    
    void assignRequest() {
        used_capacity++;
    }
    
    // Calculate load ratio (used/total capacity)
    double getLoadRatio() const {
        return capacity > 0 ? static_cast<double>(used_capacity) / capacity : 1.0;
    }
    
    // Remaining capacity
    int getRemainingCapacity() const {
        return capacity - used_capacity;
    }
};

std::vector<int> distribute_load(const std::vector<int>& server_capacities, 
                                 const std::vector<int>& requests) {
    if (server_capacities.empty() || requests.empty()) {
        return std::vector<int>(server_capacities.size(), 0);
    }
    
    // Initialize servers
    std::vector<Server> servers;
    for (size_t i = 0; i < server_capacities.size(); ++i) {
        servers.emplace_back(i, server_capacities[i]);
    }
    
    // Count requests by priority
    std::unordered_map<int, int> priority_counts;
    for (int priority : requests) {
        priority_counts[priority]++;
    }
    
    // Create a vector of priorities in descending order
    std::vector<int> priorities;
    for (const auto& pair : priority_counts) {
        priorities.push_back(pair.first);
    }
    std::sort(priorities.begin(), priorities.end(), std::greater<int>());
    
    // Process requests by priority (highest first)
    for (int priority : priorities) {
        int requestsOfThisPriority = priority_counts[priority];
        
        // Create a min-heap of servers ordered by load ratio
        auto serverComparator = [](const Server* a, const Server* b) {
            // If load ratios are close, prefer servers with more remaining capacity
            if (std::abs(a->getLoadRatio() - b->getLoadRatio()) < 0.001) {
                return a->getRemainingCapacity() < b->getRemainingCapacity();
            }
            return a->getLoadRatio() > b->getLoadRatio();
        };
        
        std::priority_queue<Server*, std::vector<Server*>, decltype(serverComparator)> 
            serverHeap(serverComparator);
        
        // Add all servers with remaining capacity to the heap
        for (auto& server : servers) {
            if (server.canAcceptRequest()) {
                serverHeap.push(&server);
            }
        }
        
        // Distribute requests of this priority to servers
        while (requestsOfThisPriority > 0 && !serverHeap.empty()) {
            Server* server = serverHeap.top();
            serverHeap.pop();
            
            server->assignRequest();
            requestsOfThisPriority--;
            
            // If server still has capacity, push it back to the heap
            if (server->canAcceptRequest()) {
                serverHeap.push(server);
            }
        }
        
        // If we couldn't assign all requests, they're dropped
    }
    
    // Collect final distribution
    std::vector<int> distribution(server_capacities.size(), 0);
    for (const auto& server : servers) {
        distribution[server.id] = server.used_capacity;
    }
    
    return distribution;
}

} // namespace load_balancer