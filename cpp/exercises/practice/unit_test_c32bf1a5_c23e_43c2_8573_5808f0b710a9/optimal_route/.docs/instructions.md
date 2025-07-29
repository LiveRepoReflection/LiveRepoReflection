## Project Name

`OptimalRoutePlanner`

## Question Description

You are tasked with designing an optimal route planning system for a delivery company operating in a large, densely populated city. The city is represented as a weighted, directed graph where:

*   Nodes represent street intersections.
*   Edges represent street segments connecting intersections.
*   Edge weights represent the *time* (in minutes) it takes to traverse that street segment, which can vary depending on traffic conditions.

The delivery company has a central depot located at a designated starting intersection. Each day, the company needs to deliver packages to a set of *N* customer locations (other intersections). You are given the following inputs:

1.  `num_intersections`: The total number of intersections in the city (numbered from 0 to `num_intersections - 1`).
2.  `edges`: A vector of tuples, where each tuple represents a directed edge in the graph: `(start_intersection, end_intersection, travel_time)`.  `travel_time` is a non-negative integer.
3.  `depot_intersection`: The integer representing the starting intersection (depot).
4.  `customer_intersections`: A vector of integers representing the intersections where deliveries need to be made.
5.  `max_route_time`: An integer representing the maximum allowable time (in minutes) for a delivery route, starting from the depot and returning to the depot.

The delivery company wants to minimize the total travel time of the delivery route while adhering to the following constraints:

*   **All customer locations must be visited exactly once.** The order of visiting customers matters.
*   The route *must* start and end at the `depot_intersection`.
*   The total travel time of the route (depot -> customer1 -> customer2 -> ... -> customerN -> depot) must not exceed `max_route_time`.

Your task is to write a function that returns the *minimum* possible total travel time for a valid delivery route. If no valid route exists that satisfies all the constraints, return `-1`.

**Constraints:**

*   1 <= `num_intersections` <= 20
*   1 <= `edges.size()` <= `num_intersections * (num_intersections - 1)` (fully connected graph)
*   0 <= `travel_time` <= 100 for each edge.
*   0 <= `depot_intersection` < `num_intersections`
*   1 <= `customer_intersections.size()` <= `num_intersections - 1`
*   1 <= `max_route_time` <= 10000
*   All `customer_intersections` are distinct and different from the `depot_intersection`.
*   The graph is guaranteed to be strongly connected.  There is a path from any intersection to any other intersection.

**Example:**

Let's say you have 4 intersections: 0 (depot), 1, 2, and 3.  Customer locations are 1 and 2.

`num_intersections = 4`

`edges = [(0, 1, 10), (0, 2, 15), (0, 3, 20), (1, 0, 10), (1, 2, 5), (1, 3, 12), (2, 0, 10), (2, 1, 5), (2, 3, 8), (3, 0, 15), (3, 1, 12), (3, 2, 8)]`

`depot_intersection = 0`

`customer_intersections = [1, 2]`

`max_route_time = 50`

Possible routes:

*   0 -> 1 -> 2 -> 0: Time = 10 + 5 + 10 = 25  (Valid)
*   0 -> 2 -> 1 -> 0: Time = 15 + 5 + 10 = 30  (Valid)

The optimal route is 0 -> 1 -> 2 -> 0 with a total travel time of 25.  Therefore, the function should return `25`.
