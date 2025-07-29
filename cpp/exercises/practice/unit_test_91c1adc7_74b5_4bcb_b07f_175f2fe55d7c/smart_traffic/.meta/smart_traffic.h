#ifndef SMART_TRAFFIC_H
#define SMART_TRAFFIC_H

#include <vector>
#include <tuple>

namespace smart_traffic {

int calculate_optimal_flow(int N, int source, int sink, 
    const std::vector<std::tuple<int, int, int, int, int, int>> &roads);

}

#endif