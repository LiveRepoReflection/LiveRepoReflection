#include "tenant_rate_limit.h"

RateLimiter::RateLimiter() {}

void RateLimiter::validateConfig(int requestLimit, int timeWindowSeconds) {
    if (requestLimit <= 0 || timeWindowSeconds <= 0) {
        throw std::invalid_argument("Request limit and time window must be positive");
    }
    if (timeWindowSeconds > 60) {
        throw std::invalid_argument("Time window must not exceed 60 seconds");
    }
    if (requestLimit > 10000) {
        throw std::invalid_argument("Request limit must not exceed 10000");
    }
}

void RateLimiter::validateTenantId(const std::string& tenantId) {
    if (tenantId.empty()) {
        throw std::invalid_argument("Tenant ID cannot be empty");
    }
}

void RateLimiter::configureTenant(const std::string& tenantId, int requestLimit, int timeWindowSeconds) {
    validateTenantId(tenantId);
    validateConfig(requestLimit, timeWindowSeconds);

    std::lock_guard<std::mutex> lock(configMutex);
    
    auto config = std::make_unique<TenantConfig>();
    config->requestLimit = requestLimit;
    config->timeWindowSeconds = timeWindowSeconds;
    config->lastUpdateTime = std::chrono::steady_clock::now();
    
    tenantConfigs[tenantId] = std::move(config);
    lruCache.touch(tenantId);
}

void RateLimiter::cleanupOldRequests(TenantConfig* config) {
    auto now = std::chrono::steady_clock::now();
    auto windowDuration = std::chrono::seconds(config->timeWindowSeconds);

    while (!config->requestTimestamps.empty()) {
        auto oldestRequest = config->requestTimestamps.front();
        if (now - oldestRequest > windowDuration) {
            config->requestTimestamps.pop();
        } else {
            break;
        }
    }
}

bool RateLimiter::isAllowed(const std::string& tenantId) {
    validateTenantId(tenantId);
    std::lock_guard<std::mutex> lock(configMutex);

    auto it = tenantConfigs.find(tenantId);
    if (it == tenantConfigs.end()) {
        throw std::runtime_error("Tenant not configured");
    }

    TenantConfig* config = it->second.get();
    lruCache.touch(tenantId);

    // Clean up old requests
    cleanupOldRequests(config);

    // Check if we're within the rate limit
    if (config->requestTimestamps.size() >= static_cast<size_t>(config->requestLimit)) {
        return false;
    }

    // Add current request
    config->requestTimestamps.push(std::chrono::steady_clock::now());
    return true;
}

void RateLimiter::LRUCache::touch(const std::string& tenantId) {
    auto it = lruMap.find(tenantId);
    
    // Remove existing entry if present
    if (it != lruMap.end()) {
        lruList.erase(it->second);
    }
    
    // Add to front of LRU list
    lruList.push_front(tenantId);
    lruMap[tenantId] = lruList.begin();
    
    // Check if we need to evict
    if (lruMap.size() > maxSize) {
        evict();
    }
}

void RateLimiter::LRUCache::evict() {
    if (!lruList.empty()) {
        auto lastTenant = lruList.back();
        lruMap.erase(lastTenant);
        lruList.pop_back();
    }
}