#ifndef NETWORK_ROUTING_H
#define NETWORK_ROUTING_H

#include <vector>
#include <tuple>

std::vector<int> find_shortest_path(int start_node, int end_node, int query_timestamp);
void init(int n, const std::vector<std::tuple<int, int, int>>& initial_latencies);
void update_latency(int u, int v, int latency);

#endif // NETWORK_ROUTING_H