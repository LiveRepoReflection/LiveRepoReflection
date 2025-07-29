#pragma once
#include <vector>
#include <tuple>

namespace network_optimize {
    // Computes the minimum total cost to build a connected communication network.
    // n: number of cities
    // b: vector of bandwidth requirements for each city
    // roads: vector of tuples (u, v, w) representing available roads with physical distance w
    // Returns the minimum total cost, or -1 if it's impossible to build a connected network.
    long long compute_minimum_cost(int n, const std::vector<int>& b, 
                                   const std::vector<std::tuple<int, int, long long>>& roads);
}