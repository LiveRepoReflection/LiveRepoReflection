#ifndef OPTIMAL_HIGHWAY_H
#define OPTIMAL_HIGHWAY_H

#include <vector>
#include <tuple>

namespace optimal_highway {
    // Function to find the minimum cost to connect all cities as early as possible
    int minimum_cost(int N, int M, const std::vector<std::vector<std::tuple<int, int, int>>>& phases);
}

#endif // OPTIMAL_HIGHWAY_H