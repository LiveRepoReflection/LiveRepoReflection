#ifndef DYNAMIC_BALANCER_H
#define DYNAMIC_BALANCER_H

#include <string>
#include <vector>

namespace dynamic_balancer {

struct Request {
    std::string payload;
};

struct ShardingRule {
    std::string algorithm;
};

class LoadBalancer {
public:
    LoadBalancer();
    void setShardingKey(const std::string& key);
    void addBackend(const std::string& name, int weight);
    void removeBackend(const std::string& name);
    std::string routeRequest(const Request& req);
    void updateHealth(const std::string& backendName, bool healthy);
    void updateShardingRule(const ShardingRule& rule);
private:
    struct Backend {
        std::string name;
        int weight;
        bool healthy;
    };

    std::vector<Backend> backends;
    std::string shardingKey;
    std::string currentAlgorithm; // "round_robin" or "consistent_hashing"
    size_t rrIndex; // round-robin index

    std::vector<Backend*> getHealthyBackends();
};

} // namespace dynamic_balancer

#endif