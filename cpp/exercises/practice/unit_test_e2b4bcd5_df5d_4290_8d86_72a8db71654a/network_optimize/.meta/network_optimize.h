#ifndef NETWORK_OPTIMIZE_H
#define NETWORK_OPTIMIZE_H

#include <vector>
#include <stdexcept>

namespace network_optimize {

double optimize_network(int N, const std::vector<std::vector<int>>& adjMatrix, int K);

}  // namespace network_optimize

#endif  // NETWORK_OPTIMIZE_H