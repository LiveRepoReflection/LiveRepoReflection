#ifndef DRONE_DELIVERY_H
#define DRONE_DELIVERY_H

#include <vector>
#include <limits>

namespace drone_delivery {

struct Street {
    int from;
    int to;
    int travel_time;
    int capacity;
};

struct DeliveryRequest {
    int start_intersection;
    int destination_intersection;
    int deadline;
    int priority;
    int arrival_time;
};

class DroneDeliverySystem {
public:
    DroneDeliverySystem(const std::vector<int>& intersections, const std::vector<Street>& streets);
    std::vector<int> plan_route(const DeliveryRequest& request);
private:
    std::vector<int> nodes;
    std::vector<std::vector<Street>> adj;
};

} // namespace drone_delivery

#endif