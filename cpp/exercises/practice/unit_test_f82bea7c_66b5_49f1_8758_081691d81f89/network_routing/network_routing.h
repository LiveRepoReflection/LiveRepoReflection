#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>

class NetworkRouter {
public:
    explicit NetworkRouter(int num_nodes);
    
    void add_link(int u, int v, int cost);
    void remove_link(int u, int v);
    std::vector<int> get_optimal_path(int start, int end);

private:
    // Implementation details to be defined
};

#endif // NETWORK_ROUTING_H