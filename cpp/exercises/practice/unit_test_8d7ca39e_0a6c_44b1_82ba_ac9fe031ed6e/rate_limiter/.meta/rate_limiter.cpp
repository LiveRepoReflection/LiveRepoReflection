#include "rate_limiter.h"
#include <algorithm>
#include <iostream>

// ==================== RateLimiter Implementation ====================

RateLimiter::RateLimiter(int rateLimit, int windowDurationMs)
    : rateLimit_(rateLimit), windowDurationMs_(windowDurationMs) {
}

bool RateLimiter::allow(const std::string& key) {
    auto now = std::chrono::steady_clock::now();
    
    // Try to find the counter for this key with a shared lock first
    {
        std::shared_lock<std::shared_mutex> readLock(mapMutex_);
        auto it = counterMap_.find(key);
        if (it != counterMap_.end()) {
            return it->second->allow(now);
        }
    }
    
    // Counter doesn't exist yet, create it with an exclusive lock
    {
        std::unique_lock<std::shared_mutex> writeLock(mapMutex_);
        // Check again in case another thread created the counter while we were waiting
        auto it = counterMap_.find(key);
        if (it == counterMap_.end()) {
            auto counter = std::make_unique<SlidingWindowCounter>(rateLimit_, windowDurationMs_);
            auto result = counter->allow(now);
            counterMap_[key] = std::move(counter);
            return result;
        } else {
            return it->second->allow(now);
        }
    }
}

// ==================== SlidingWindowCounter Implementation ====================

RateLimiter::SlidingWindowCounter::SlidingWindowCounter(int rateLimit, int windowDurationMs)
    : rateLimit_(rateLimit), windowDuration_(std::chrono::milliseconds(windowDurationMs)), currentCount_(0) {
}

bool RateLimiter::SlidingWindowCounter::allow(std::chrono::steady_clock::time_point now) {
    // Remove expired entries from the deque
    auto expireTime = now - windowDuration_;
    while (!requests_.empty() && requests_.front().timestamp < expireTime) {
        currentCount_ -= requests_.front().count;
        requests_.pop_front();
    }

    // If we're under the rate limit, allow the request
    if (currentCount_ < rateLimit_) {
        // Check if we can merge with the last entry (if it's very recent)
        if (!requests_.empty() && 
            (now - requests_.back().timestamp) < std::chrono::milliseconds(10)) {
            requests_.back().count++;
        } else {
            requests_.push_back({now, 1});
        }
        currentCount_++;
        return true;
    }
    
    return false;
}

// ==================== DistributedRateLimiter Implementation ====================

DistributedRateLimiter::DistributedRateLimiter(int rateLimit, int windowDurationMs,
                                           const std::string& redisHost, int redisPort)
    : RateLimiter(rateLimit, windowDurationMs) {
    // Initialize Redis connection
    redisConn_ = std::make_unique<RedisConnection>();
    redisConn_->host = redisHost;
    redisConn_->port = redisPort;
    redisConn_->connected = true; // In a real implementation, we would actually connect
    
    std::cout << "Initialized distributed rate limiter with Redis at " 
              << redisHost << ":" << redisPort << std::endl;
}

DistributedRateLimiter::~DistributedRateLimiter() {
    // Cleanup Redis connection (if needed)
    if (redisConn_ && redisConn_->connected) {
        // In a real implementation, we would disconnect
        std::cout << "Disconnected from Redis" << std::endl;
    }
}

bool DistributedRateLimiter::allow(const std::string& key) {
    // Call the Redis-based implementation
    return allowWithRedis(key);
}

bool DistributedRateLimiter::allowWithRedis(const std::string& key) {
    // This is a simplified simulation of a Redis-based sliding window log algorithm
    auto now = std::chrono::steady_clock::now();
    auto windowStart = now - std::chrono::milliseconds(windowDurationMs_);
    
    std::string redisKey = "rate_limit:" + key;
    
    // In a real implementation, we would use Redis MULTI/EXEC for atomicity
    // For simulation, we'll use a local mutex
    std::lock_guard<std::mutex> lock(redisConn_->redisMutex);
    
    auto& requestLog = redisConn_->requestLog[redisKey];
    
    // Remove expired entries
    while (!requestLog.empty() && requestLog.front() < windowStart) {
        requestLog.pop_front();
    }
    
    // Check if we're under the limit
    if (static_cast<int>(requestLog.size()) < rateLimit_) {
        requestLog.push_back(now);
        
        // In a real implementation, we would also set an expiration on the Redis key
        // EXPIRE redisKey windowDurationMs_/1000
        
        return true;
    }
    
    return false;
}