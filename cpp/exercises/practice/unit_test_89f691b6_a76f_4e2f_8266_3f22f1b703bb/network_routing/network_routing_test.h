#ifndef NETWORK_ROUTING_TEST_H
#define NETWORK_ROUTING_TEST_H

#include <vector>

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
};

#endif // NETWORK_ROUTING_TEST_H