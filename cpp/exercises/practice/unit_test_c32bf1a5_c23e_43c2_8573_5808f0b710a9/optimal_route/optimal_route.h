#ifndef OPTIMAL_ROUTE_H
#define OPTIMAL_ROUTE_H

#include <vector>
#include <tuple>

namespace optimal_route {
    // Function to find the minimum travel time for a valid delivery route
    // Returns -1 if no valid route exists
    int min_travel_time(
        int num_intersections,
        const std::vector<std::tuple<int, int, int>>& edges,
        int depot_intersection,
        const std::vector<int>& customer_intersections,
        int max_route_time
    );
}

#endif // OPTIMAL_ROUTE_H