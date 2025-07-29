#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <unordered_map>

class NetworkRouter {
public:
    explicit NetworkRouter(int num_nodes);
    
    void add_link(int u, int v, int cost);
    void remove_link(int u, int v);
    std::vector<int> get_optimal_path(int start, int end);

private:
    class Implementation;
    int num_nodes_;
    std::vector<std::unordered_map<int, int>> adjacency_list_;
};

#endif // NETWORK_ROUTING_H