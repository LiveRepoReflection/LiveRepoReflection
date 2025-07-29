#ifndef NETWORK_OPTIMIZE_H
#define NETWORK_OPTIMIZE_H

#include <vector>
#include <tuple>

namespace network_optimize {
    bool can_route_all(int N, 
                      const std::vector<std::tuple<int, int, int>>& edges,
                      const std::vector<std::tuple<int, int, int>>& queries);
}

#endif // NETWORK_OPTIMIZE_H