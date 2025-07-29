#ifndef NETWORK_RESILIENCE_H
#define NETWORK_RESILIENCE_H

#include <tuple>
#include <vector>

namespace network_resilience {
    int maximum_resilience(int N, const std::vector<std::tuple<int, int, int>> &edges);
}

#endif