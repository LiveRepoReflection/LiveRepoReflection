#ifndef DRONE_DELIVERY_H
#define DRONE_DELIVERY_H

#include <vector>
#include <utility>

std::vector<int> schedule_deliveries(
    int num_nodes,
    const std::vector<std::vector<std::pair<int, int>>>& adjacency_list,
    const std::vector<std::vector<int>>& delivery_requests,
    int drone_capacity,
    int drone_flight_time
);

#endif // DRONE_DELIVERY_H