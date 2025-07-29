#include "social_reach.h"
#include <queue>
#include <unordered_map>
#include <unordered_set>

std::set<int> socialReachKHop(
    int startingUserID,
    int k,
    const std::function<std::tuple<std::vector<int>, std::vector<int>, std::vector<std::string>>(int)>& networkData
) {
    // Set to store reachable user IDs
    std::set<int> reachableUsers;
    
    // Cache for network data to avoid redundant API calls
    std::unordered_map<int, std::vector<int>> followeeCache;
    
    // Set for tracking visited users to avoid cycles
    std::unordered_set<int> visited;

    // BFS queue with user ID and remaining hops
    std::queue<std::pair<int, int>> queue;
    
    // Start with the initial user with k hops remaining
    queue.push({startingUserID, k});
    visited.insert(startingUserID);
    reachableUsers.insert(startingUserID);
    
    while (!queue.empty()) {
        auto [currentUserID, remainingHops] = queue.front();
        queue.pop();
        
        // Skip further exploration if no hops left
        if (remainingHops <= 0) continue;
        
        // Check if we've already fetched this user's data
        if (followeeCache.find(currentUserID) == followeeCache.end()) {
            // Fetch network data for current user
            auto userData = networkData(currentUserID);
            
            // Cache the followees (we only need followees for traversal)
            followeeCache[currentUserID] = std::get<1>(userData);
        }
        
        // Process each followee
        for (int followeeID : followeeCache[currentUserID]) {
            // If user hasn't been visited yet
            if (visited.find(followeeID) == visited.end()) {
                // Mark as visited
                visited.insert(followeeID);
                
                // Add to reachable users
                reachableUsers.insert(followeeID);
                
                // Add to queue for further exploration with one fewer hop
                queue.push({followeeID, remainingHops - 1});
            }
        }
    }
    
    return reachableUsers;
}