#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <unordered_map>
#include <queue>
#include <climits>
#include <algorithm>

class NetworkRouting {
public:
    void initialize(int n);
    void add_connection(int node1, int node2, int latency, int bandwidth);
    void remove_connection(int node1, int node2);
    std::vector<int> find_best_path(int start_node, int end_node, int min_bandwidth, int max_latency);

private:
    struct Edge {
        int to;
        int latency;
        int bandwidth;
    };

    struct PathInfo {
        int node;
        int hops;
        int total_latency;
        std::vector<int> path;
    };

    std::unordered_map<int, std::vector<Edge>> graph;
    int node_count;
};

#endif // NETWORK_ROUTING_H