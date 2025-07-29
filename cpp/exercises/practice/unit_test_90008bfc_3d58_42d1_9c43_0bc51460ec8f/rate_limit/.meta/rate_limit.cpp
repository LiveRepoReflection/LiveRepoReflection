#include "rate_limit.h"
#include <stdexcept>

RateLimiter::RateLimiter(size_t maxRequestsPerSecond)
    : maxRequests(maxRequestsPerSecond), timeWindow(1) {
    if (maxRequestsPerSecond == 0) {
        throw std::invalid_argument("Max requests per second must be greater than 0");
    }
}

bool RateLimiter::allowRequest(const std::string& clientId, const std::string& resourceId) {
    validateInput(clientId, resourceId);
    
    std::string key = createKey(clientId, resourceId);
    auto bucket = getOrCreateBucket(key);
    
    std::lock_guard<std::mutex> lock(bucket->mutex);
    
    // Clean up expired requests
    cleanupOldRequests(*bucket);
    
    // Check if we're under the limit
    if (bucket->requests.size() < maxRequests) {
        bucket->requests.push(std::chrono::steady_clock::now());
        return true;
    }
    
    return false;
}

void RateLimiter::validateInput(const std::string& clientId, const std::string& resourceId) {
    if (clientId.empty()) {
        throw std::invalid_argument("Client ID cannot be empty");
    }
    if (resourceId.empty()) {
        throw std::invalid_argument("Resource ID cannot be empty");
    }
    if (clientId.length() > 1000 || resourceId.length() > 1000) {
        throw std::invalid_argument("ID length exceeds maximum allowed length");
    }
}

std::string RateLimiter::createKey(const std::string& clientId, const std::string& resourceId) {
    return clientId + ":" + resourceId;
}

void RateLimiter::cleanupOldRequests(TokenBucket& bucket) {
    auto now = std::chrono::steady_clock::now();
    while (!bucket.requests.empty()) {
        auto& oldestRequest = bucket.requests.front();
        if (now - oldestRequest > timeWindow) {
            bucket.requests.pop();
        } else {
            break;
        }
    }
}

std::shared_ptr<RateLimiter::TokenBucket> RateLimiter::getOrCreateBucket(const std::string& key) {
    // First try reading with shared lock
    {
        std::shared_lock<std::shared_mutex> readLock(mapMutex);
        auto it = rateLimits.find(key);
        if (it != rateLimits.end()) {
            return it->second;
        }
    }
    
    // If not found, upgrade to unique lock and create
    std::unique_lock<std::shared_mutex> writeLock(mapMutex);
    auto& bucket = rateLimits[key];
    if (!bucket) {
        bucket = std::make_shared<TokenBucket>();
    }
    return bucket;
}