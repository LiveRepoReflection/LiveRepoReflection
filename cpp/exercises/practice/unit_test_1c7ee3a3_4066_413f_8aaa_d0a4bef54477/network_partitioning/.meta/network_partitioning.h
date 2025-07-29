#ifndef NETWORK_PARTITIONING_H
#define NETWORK_PARTITIONING_H

#include <vector>
#include <utility>

namespace network_partitioning {

int min_additional_servers(int N, const std::vector<std::pair<int, int>>& edges, const std::vector<std::pair<int, int>>& compromised);

}

#endif  // NETWORK_PARTITIONING_H