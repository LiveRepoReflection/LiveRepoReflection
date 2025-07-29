#if !defined(ROUTE_OPTIMIZER_H)
#define ROUTE_OPTIMIZER_H

#include <tuple>
#include <vector>

/**
 * Find the least congested route from start to destination that satisfies time and toll constraints.
 * 
 * @param n Number of intersections in the city (numbered 0 to n-1)
 * @param edges Vector of tuples (start_intersection, end_intersection, travel_time, toll_cost, congestion_level)
 * @param start Starting intersection
 * @param destination Destination intersection
 * @param max_travel_time Maximum allowed travel time (in seconds)
 * @param max_toll_cost Maximum allowed toll cost (in USD)
 * @return Sum of congestion levels along the least congested route, or -1 if no valid route exists
 */
int solve(int n, const std::vector<std::tuple<int, int, int, int, int>>& edges, 
          int start, int destination, int max_travel_time, int max_toll_cost);

#endif  // ROUTE_OPTIMIZER_H