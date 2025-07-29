#ifndef TENANT_RATE_LIMIT_H
#define TENANT_RATE_LIMIT_H

#include <string>
#include <unordered_map>
#include <mutex>
#include <chrono>
#include <queue>
#include <list>
#include <memory>
#include <stdexcept>

class RateLimiter {
public:
    RateLimiter();
    void configureTenant(const std::string& tenantId, int requestLimit, int timeWindowSeconds);
    bool isAllowed(const std::string& tenantId);

private:
    struct TenantConfig {
        int requestLimit;
        int timeWindowSeconds;
        std::queue<std::chrono::steady_clock::time_point> requestTimestamps;
        std::chrono::steady_clock::time_point lastUpdateTime;
    };

    struct LRUCache {
        std::list<std::string> lruList;
        std::unordered_map<std::string, std::list<std::string>::iterator> lruMap;
        const size_t maxSize = 1000000;  // Maximum number of tenants to store

        void touch(const std::string& tenantId);
        void evict();
    };

    std::unordered_map<std::string, std::unique_ptr<TenantConfig>> tenantConfigs;
    std::mutex configMutex;
    LRUCache lruCache;

    void cleanupOldRequests(TenantConfig* config);
    void validateConfig(int requestLimit, int timeWindowSeconds);
    void validateTenantId(const std::string& tenantId);
};

#endif