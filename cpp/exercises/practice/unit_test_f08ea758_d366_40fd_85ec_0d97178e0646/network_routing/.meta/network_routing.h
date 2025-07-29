#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <map>
#include <set>
#include <climits>

class NetworkRouting {
public:
    void initialize(int N, const std::vector<std::pair<std::pair<int, int>, int>>& edges);
    void process_update(int timestamp, int node1, int node2, int new_cost);
    int query(int query_timestamp, int start_node, int end_node);

private:
    struct EdgeUpdate {
        int timestamp;
        int cost;
        bool operator<(const EdgeUpdate& other) const {
            return timestamp < other.timestamp;
        }
    };

    struct Edge {
        int node;
        mutable std::set<EdgeUpdate> updates;
    };

    int num_nodes;
    std::map<std::pair<int, int>, std::set<EdgeUpdate>> edge_updates;
    std::map<std::pair<int, int>, std::vector<Edge>> adj_list;

    int get_current_cost(int node1, int node2, int timestamp) const;
    void build_graph_at_timestamp(int timestamp, std::vector<std::vector<int>>& graph) const;
};

#endif // NETWORK_ROUTING_H