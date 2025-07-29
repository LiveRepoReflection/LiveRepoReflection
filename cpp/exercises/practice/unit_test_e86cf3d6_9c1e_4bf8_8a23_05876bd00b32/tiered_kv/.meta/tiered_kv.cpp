#include "tiered_kv.h"
#include <unordered_map>
#include <list>
#include <mutex>
#include <thread>
#include <chrono>

namespace tiered_kv {

// LRU Cache Implementation
class LRUCache {
public:
    LRUCache(size_t capacity) : capacity_(capacity) {}

    std::optional<std::string> get(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = cacheItemsMap.find(key);
        if (it == cacheItemsMap.end())
            return std::nullopt;
        // Move the key to the front (most recently used)
        cacheItemsList.splice(cacheItemsList.begin(), cacheItemsList, it->second.second);
        return it->second.first;
    }

    void put(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = cacheItemsMap.find(key);
        if (it != cacheItemsMap.end()) {
            // Update value and move key to the front
            it->second.first = value;
            cacheItemsList.splice(cacheItemsList.begin(), cacheItemsList, it->second.second);
        } else {
            if (cacheItemsMap.size() >= capacity_) {
                // Remove least recently used item (at the back)
                std::string lruKey = cacheItemsList.back();
                cacheItemsList.pop_back();
                cacheItemsMap.erase(lruKey);
            }
            cacheItemsList.push_front(key);
            cacheItemsMap[key] = {value, cacheItemsList.begin()};
        }
    }

    void deleteKey(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = cacheItemsMap.find(key);
        if (it != cacheItemsMap.end()) {
            cacheItemsList.erase(it->second.second);
            cacheItemsMap.erase(it);
        }
    }

private:
    size_t capacity_;
    std::list<std::string> cacheItemsList;
    std::unordered_map<std::string, std::pair<std::string, std::list<std::string>::iterator>> cacheItemsMap;
    std::mutex mtx_;
};

// Singleton instance for LRU Cache with a fixed capacity (simulate limited memory tier)
static LRUCache cache(100);

// Simulated Persistent Storage (Disk Tier)
class PersistentStore {
public:
    std::optional<std::string> get(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto it = store.find(key);
        if (it == store.end())
            return std::nullopt;
        return it->second;
    }

    void put(const std::string& key, const std::string& value) {
        std::lock_guard<std::mutex> lock(mtx_);
        store[key] = value;
    }

    void deleteKey(const std::string& key) {
        std::lock_guard<std::mutex> lock(mtx_);
        store.erase(key);
    }

private:
    std::unordered_map<std::string, std::string> store;
    std::mutex mtx_;
};

// Singleton instance for Persistent Storage
static PersistentStore persistentStore;

bool put(const std::string& key, const std::string& value) {
    // Update in Memory Tier (LRU Cache) first
    cache.put(key, value);
    
    // Asynchronously update Persistent Tier
    std::thread([key, value]() {
        // Simulate asynchronous disk write delay
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        persistentStore.put(key, value);
    }).detach();
    
    return true;
}

std::optional<std::string> get(const std::string& key) {
    // Attempt to retrieve from Memory Tier first
    auto value = cache.get(key);
    if (value.has_value())
        return value;
    
    // Retrieve from Persistent Tier if not found in cache
    auto persistentValue = persistentStore.get(key);
    if (persistentValue.has_value()) {
        // Update cache with this value for future accesses
        cache.put(key, persistentValue.value());
    }
    return persistentValue;
}

bool deleteKey(const std::string& key) {
    // Remove from Memory Tier
    cache.deleteKey(key);
    
    // Asynchronously delete from Persistent Tier
    std::thread([key]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        persistentStore.deleteKey(key);
    }).detach();
    
    return true;
}

} // namespace tiered_kv