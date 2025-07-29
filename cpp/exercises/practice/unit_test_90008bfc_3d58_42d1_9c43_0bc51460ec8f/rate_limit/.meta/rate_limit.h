#ifndef RATE_LIMIT_H
#define RATE_LIMIT_H

#include <string>
#include <unordered_map>
#include <mutex>
#include <chrono>
#include <queue>
#include <memory>
#include <shared_mutex>

class RateLimiter {
public:
    RateLimiter(size_t maxRequestsPerSecond = 1);
    bool allowRequest(const std::string& clientId, const std::string& resourceId);

private:
    struct TokenBucket {
        std::queue<std::chrono::steady_clock::time_point> requests;
        std::mutex mutex;
    };

    struct ClientResource {
        std::string key;
        std::shared_ptr<TokenBucket> bucket;
    };

    void validateInput(const std::string& clientId, const std::string& resourceId);
    std::string createKey(const std::string& clientId, const std::string& resourceId);
    void cleanupOldRequests(TokenBucket& bucket);
    std::shared_ptr<TokenBucket> getOrCreateBucket(const std::string& key);

    const size_t maxRequests;
    const std::chrono::seconds timeWindow;
    std::unordered_map<std::string, std::shared_ptr<TokenBucket>> rateLimits;
    mutable std::shared_mutex mapMutex;
};

#endif