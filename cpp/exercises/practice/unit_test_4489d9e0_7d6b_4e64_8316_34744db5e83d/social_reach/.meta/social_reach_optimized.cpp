#include "social_reach.h"
#include <queue>
#include <unordered_map>
#include <unordered_set>

/*
 * This is an optimized implementation that uses a layered BFS approach to minimize
 * the number of API calls while correctly handling both the k-hop constraint and cycles.
 */
std::set<int> socialReachKHop(
    int startingUserID,
    int k,
    const std::function<std::tuple<std::vector<int>, std::vector<int>, std::vector<std::string>>(int)>& networkData
) {
    // Use a sorted set for the final result (per requirement)
    std::set<int> reachableUsers = {startingUserID};
    
    // Early return if k is 0
    if (k <= 0) return reachableUsers;
    
    // Track users at each level of BFS to implement layer-by-layer exploration
    std::unordered_set<int> currentFrontier = {startingUserID};
    
    // Track all visited users to avoid cycles
    std::unordered_set<int> allVisited = {startingUserID};
    
    // Cache for network data to avoid redundant API calls
    std::unordered_map<int, std::vector<int>> followeeCache;
    
    // Process one hop at a time up to k hops
    for (int hop = 0; hop < k; hop++) {
        // Next layer of users to explore
        std::unordered_set<int> nextFrontier;
        
        // Process all users in the current layer
        for (int userID : currentFrontier) {
            // Fetch followees if not already cached
            if (followeeCache.find(userID) == followeeCache.end()) {
                auto userData = networkData(userID);
                followeeCache[userID] = std::get<1>(userData); // Store followees
            }
            
            // Process each followee
            for (int followeeID : followeeCache[userID]) {
                // If not already visited in any previous layer
                if (allVisited.find(followeeID) == allVisited.end()) {
                    nextFrontier.insert(followeeID);
                    allVisited.insert(followeeID);
                    reachableUsers.insert(followeeID);
                }
            }
        }
        
        // If no new users to explore, terminate early
        if (nextFrontier.empty()) {
            break;
        }
        
        // Update current frontier to the next layer
        currentFrontier = std::move(nextFrontier);
    }
    
    return reachableUsers;
}