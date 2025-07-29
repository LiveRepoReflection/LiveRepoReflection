#ifndef NETWORK_ROUTE_H
#define NETWORK_ROUTE_H

#include <vector>
#include <tuple>

/**
 * Finds the optimal route from source to destination that minimizes average latency per hop.
 * 
 * @param N Number of nodes in the network (0 to N-1)
 * @param links Vector of tuples (u, v, latency) representing bidirectional links
 * @param S Source node
 * @param D Destination node
 * @return Vector of nodes representing the optimal path from S to D, or empty if no path exists
 */
std::vector<int> find_optimal_route(int N, 
                                   const std::vector<std::tuple<int, int, int>>& links,
                                   int S, 
                                   int D);

#endif // NETWORK_ROUTE_H