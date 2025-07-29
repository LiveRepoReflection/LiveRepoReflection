#ifndef NETWORK_CAPACITY_H
#define NETWORK_CAPACITY_H

#include <vector>
using std::vector;

namespace network_capacity {

struct Edge {
    int u;
    int v;
    int capacity;
    double failure_probability;
};

double max_guaranteed_bandwidth(int N, const vector<Edge>& edges, int S, int D);

} // namespace network_capacity

#endif