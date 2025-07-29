#ifndef OPTIMAL_TRAFFIC_H
#define OPTIMAL_TRAFFIC_H

#include <vector>
#include <tuple>

namespace optimal_traffic {

int earliest_arrival(int num_intersections,
                     const std::vector<std::tuple<int, int, int, int>> &roads,
                     const std::vector<int> &start_intersections,
                     int destination,
                     const std::vector<std::tuple<int, int, int, int, int>> &capacity_updates);

}

#endif // OPTIMAL_TRAFFIC_H