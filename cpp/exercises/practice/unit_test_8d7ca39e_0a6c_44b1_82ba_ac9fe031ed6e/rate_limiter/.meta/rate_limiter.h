#pragma once

#include <string>
#include <chrono>
#include <unordered_map>
#include <mutex>
#include <memory>
#include <deque>
#include <atomic>
#include <shared_mutex>

class RateLimiter {
public:
    // Constructor: takes the rate limit (requests per window),
    // window duration (in milliseconds)
    RateLimiter(int rateLimit, int windowDurationMs);
    virtual ~RateLimiter() = default;

    // Attempts to acquire a permit for the given key.
    // Returns true if the request is allowed, false if it is rate limited.
    virtual bool allow(const std::string& key);

protected:
    // Implementation of sliding window counter algorithm
    class SlidingWindowCounter {
    public:
        SlidingWindowCounter(int rateLimit, int windowDurationMs);
        bool allow(std::chrono::steady_clock::time_point now);

    private:
        int rateLimit_;
        std::chrono::milliseconds windowDuration_;
        struct TimeRequest {
            std::chrono::steady_clock::time_point timestamp;
            int count;
        };
        std::deque<TimeRequest> requests_;
        int currentCount_;
    };

    int rateLimit_;
    int windowDurationMs_;
    mutable std::shared_mutex mapMutex_; // Reader-writer lock for better concurrency
    std::unordered_map<std::string, std::unique_ptr<SlidingWindowCounter>> counterMap_;
};

// Distributed rate limiter that uses Redis as a backend
class DistributedRateLimiter : public RateLimiter {
public:
    // Constructor that takes Redis connection information
    DistributedRateLimiter(int rateLimit, int windowDurationMs,
                         const std::string& redisHost = "localhost", 
                         int redisPort = 6379);
    ~DistributedRateLimiter() override;

    bool allow(const std::string& key) override;

private:
    // Placeholder for Redis connection
    // In a real implementation, this would be replaced with actual Redis client
    struct RedisConnection {
        std::string host;
        int port;
        bool connected;
        // For demonstration purposes, we'll use a local cache to simulate Redis
        std::unordered_map<std::string, std::deque<std::chrono::steady_clock::time_point>> requestLog;
        std::mutex redisMutex;
    };
    std::unique_ptr<RedisConnection> redisConn_;

    // Implementation of Redis-based sliding window log algorithm
    bool allowWithRedis(const std::string& key);
};