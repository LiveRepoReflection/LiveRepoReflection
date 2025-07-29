#pragma once

#include <vector>
#include <tuple>

namespace network_reliability {

/*
 * Computes the probability that a network of n nodes is fully connected.
 * The network is given as a vector of edges, where each edge is represented
 * as a tuple (u, v, p) meaning that there is a bidirectional link between node u and v
 * with operational probability p.
 * Nodes are labeled from 0 to n-1.
 */
double compute_network_reliability(int n, const std::vector<std::tuple<int, int, double>>& edges);

}  // namespace network_reliability