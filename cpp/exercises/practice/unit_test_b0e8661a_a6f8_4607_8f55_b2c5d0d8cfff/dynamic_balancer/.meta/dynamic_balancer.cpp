#include "dynamic_balancer.h"
#include <stdexcept>
#include <functional>
#include <algorithm>

namespace dynamic_balancer {

LoadBalancer::LoadBalancer() : shardingKey(""), currentAlgorithm("round_robin"), rrIndex(0) { }

void LoadBalancer::setShardingKey(const std::string& key) {
    shardingKey = key;
}

void LoadBalancer::addBackend(const std::string& name, int weight) {
    // Check if backend already exists
    for (const auto& backend : backends) {
        if (backend.name == name) {
            return; // Already exists, do nothing
        }
    }
    Backend b;
    b.name = name;
    b.weight = weight;
    b.healthy = true;
    backends.push_back(b);
}

void LoadBalancer::removeBackend(const std::string& name) {
    auto it = std::remove_if(backends.begin(), backends.end(), [&name](const Backend& b) {
        return b.name == name;
    });
    backends.erase(it, backends.end());
}

std::vector<LoadBalancer::Backend*> LoadBalancer::getHealthyBackends() {
    std::vector<Backend*> healthy;
    for (auto &backend : backends) {
        if (backend.healthy) {
            healthy.push_back(&backend);
        }
    }
    return healthy;
}

std::string LoadBalancer::routeRequest(const Request& req) {
    std::vector<Backend*> healthyBackends = getHealthyBackends();
    if (healthyBackends.empty()) {
        throw std::runtime_error("No healthy backend servers available");
    }
    
    // Choose backend based on the currently set algorithm
    if (currentAlgorithm == "consistent_hashing") {
        std::hash<std::string> hasher;
        size_t hashValue = hasher(req.payload);
        size_t index = hashValue % healthyBackends.size();
        return healthyBackends[index]->name;
    } else { // Default to round robin
        std::string selected = healthyBackends[rrIndex % healthyBackends.size()]->name;
        rrIndex = (rrIndex + 1) % healthyBackends.size();
        return selected;
    }
}

void LoadBalancer::updateHealth(const std::string& backendName, bool healthy) {
    for (auto &backend : backends) {
        if (backend.name == backendName) {
            backend.healthy = healthy;
            return;
        }
    }
    // If backend is not found, do nothing.
}

void LoadBalancer::updateShardingRule(const ShardingRule& rule) {
    if (!rule.algorithm.empty()) {
        currentAlgorithm = rule.algorithm;
    }
}

} // namespace dynamic_balancer