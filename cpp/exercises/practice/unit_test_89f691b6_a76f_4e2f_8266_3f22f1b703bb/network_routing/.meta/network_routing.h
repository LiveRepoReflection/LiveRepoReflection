#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <unordered_map>

struct Link {
    int u;
    int v;
    int cost;
};

struct Update {
    int u;
    int v;
    int new_cost;
};

class NetworkRouter {
public:
    NetworkRouter(int n, const std::vector<Link>& links);
    int findOptimalPath(int source, int dest, const std::vector<Update>& updates);

private:
    int n_;
    std::vector<std::vector<std::pair<int, int>>> adj_list_;
    std::unordered_map<int, std::unordered_map<int, int>> edge_costs_;
    
    void updateNetwork(const std::vector<Update>& updates);
    int dijkstra(int source, int dest);
};

#endif // NETWORK_ROUTING_H