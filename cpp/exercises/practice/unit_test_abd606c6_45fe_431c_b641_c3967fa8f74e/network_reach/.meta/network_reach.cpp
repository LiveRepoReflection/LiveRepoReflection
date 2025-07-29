#include "network_reach.h"
#include <queue>
#include <unordered_map>
#include <cmath>

// Calculate Jaccard similarity between two sets of strings
double calculateJaccardIndex(const std::unordered_set<std::string>& set1, 
                           const std::unordered_set<std::string>& set2) {
    if (set1.empty() && set2.empty()) return 0.0;
    
    // Calculate intersection
    int intersection = 0;
    for (const auto& elem : set1) {
        if (set2.find(elem) != set2.end()) {
            intersection++;
        }
    }
    
    // Calculate union
    int union_size = set1.size() + set2.size() - intersection;
    
    return static_cast<double>(intersection) / union_size;
}

int estimateReach(const std::vector<int>& users,
                  const std::vector<std::pair<int, int>>& follows,
                  const std::unordered_map<int, std::pair<std::unordered_set<std::string>, double>>& userProfiles,
                  const std::pair<int, std::unordered_set<std::string>>& post,
                  int iterations) {
    
    if (users.empty() || iterations < 0) return 0;
    
    // Build adjacency list for the network
    std::unordered_map<int, std::vector<int>> adjacencyList;
    for (const auto& edge : follows) {
        adjacencyList[edge.first].push_back(edge.second);
    }
    
    // Track users who have seen the post
    std::unordered_set<int> reached;
    
    // Track users who might share in current iteration
    std::queue<int> currentQueue;
    
    // Start with the poster
    int posterId = post.first;
    if (userProfiles.find(posterId) != userProfiles.end()) {
        reached.insert(posterId);
        currentQueue.push(posterId);
    }
    
    // Process each iteration
    for (int iter = 0; iter < iterations; ++iter) {
        std::queue<int> nextQueue;
        
        // Process all users in current iteration
        while (!currentQueue.empty()) {
            int currentUser = currentQueue.front();
            currentQueue.pop();
            
            // Skip if user doesn't exist in profiles
            if (userProfiles.find(currentUser) == userProfiles.end()) continue;
            
            // Calculate probability of sharing
            double interestAlignment = calculateJaccardIndex(
                userProfiles.at(currentUser).first,
                post.second
            );
            double activityScore = userProfiles.at(currentUser).second;
            double sharingProbability = interestAlignment * activityScore;
            
            // Process followers
            for (int follower : adjacencyList[currentUser]) {
                // Skip if already reached
                if (reached.find(follower) != reached.end()) continue;
                
                // Determine if post is shared based on probability
                double random = static_cast<double>(rand()) / RAND_MAX;
                if (random < sharingProbability) {
                    reached.insert(follower);
                    nextQueue.push(follower);
                }
            }
        }
        
        // Update queue for next iteration
        currentQueue = nextQueue;
        
        // Early termination if no new shares
        if (currentQueue.empty()) break;
    }
    
    return reached.size();
}