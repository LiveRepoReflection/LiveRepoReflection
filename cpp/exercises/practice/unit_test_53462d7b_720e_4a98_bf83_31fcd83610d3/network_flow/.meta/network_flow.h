#ifndef NETWORK_FLOW_H
#define NETWORK_FLOW_H

#include <tuple>
#include <vector>

namespace network_flow {

void init_network(int N, const std::vector<std::tuple<int, int, int>>& edges);
void add_request(int request_id, int source, int destination, int demand);
void remove_request(int request_id);
int query_request(int request_id);

} // namespace network_flow

#endif // NETWORK_FLOW_H