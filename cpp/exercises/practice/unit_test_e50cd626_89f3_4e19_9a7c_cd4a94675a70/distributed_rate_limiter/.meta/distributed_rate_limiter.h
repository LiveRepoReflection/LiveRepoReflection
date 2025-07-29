#ifndef DISTRIBUTED_RATE_LIMITER_H
#define DISTRIBUTED_RATE_LIMITER_H

#include <string>
#include <deque>
#include <unordered_map>

class RateLimiter {
public:
    RateLimiter();
    void setRateLimit(const std::string &userID, int maxRequests, int windowSeconds);
    bool allowRequest(const std::string &userID, int timestamp);
private:
    struct RateLimitConfig {
        int maxRequests;
        int windowSeconds;
    };
    std::unordered_map<std::string, RateLimitConfig> configMap;
    std::unordered_map<std::string, std::deque<int>> userRequests;
};

#endif // DISTRIBUTED_RATE_LIMITER_H