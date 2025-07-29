#if !defined(DRONE_DELIVERY_H)
#define DRONE_DELIVERY_H

#include <vector>
#include <tuple>
#include <utility>

namespace drone_delivery {

int find_earliest_arrival_time(
    int N,
    const std::vector<std::tuple<int, int, int>>& edges,
    const std::vector<std::pair<int, int>>& time_windows,
    const std::vector<int>& start_locations,
    int target_location
);

}  // namespace drone_delivery

#endif // DRONE_DELIVERY_H