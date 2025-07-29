#include "distributed_rate_limiter.h"

RateLimiter::RateLimiter() {
    // No initialization needed here.
}

void RateLimiter::setRateLimit(const std::string &userID, int maxRequests, int windowSeconds) {
    configMap[userID] = RateLimitConfig{maxRequests, windowSeconds};
    if (userRequests.find(userID) == userRequests.end()) {
        userRequests[userID] = std::deque<int>();
    }
}

bool RateLimiter::allowRequest(const std::string &userID, int timestamp) {
    // If no rate limit is defined for the user, deny by default.
    if (configMap.find(userID) == configMap.end()) {
        return false;
    }
    
    RateLimitConfig config = configMap[userID];
    std::deque<int> &timestamps = userRequests[userID];

    // Purge timestamps that are outside the current window
    while (!timestamps.empty() && timestamps.front() <= timestamp - config.windowSeconds) {
        timestamps.pop_front();
    }

    if (static_cast<int>(timestamps.size()) < config.maxRequests) {
        timestamps.push_back(timestamp);
        return true;
    }
    return false;
}