## Project Name

`OptimalRoutePlanning`

## Question Description

You are tasked with designing an optimal route planning system for a delivery service operating in a densely populated urban environment. The city is represented as a directed graph where nodes represent street intersections and edges represent street segments. Each street segment has a travel time (in minutes) and a congestion score (an integer representing the level of traffic).

Given a set of delivery requests, your system must determine the most efficient delivery route for each driver, considering both travel time and congestion.

**Input:**

*   **City Graph:** A directed graph represented as an adjacency list. Each node (intersection) is identified by a unique integer ID. Each edge (street segment) is represented as a tuple `(destination_node_id, travel_time, congestion_score)`.  The graph has `N` nodes and `M` edges.
*   **Delivery Requests:** A list of delivery requests. Each request is represented as a tuple `(start_node_id, end_node_id, priority)`. `priority` is an integer where higher values mean higher priority.
*   **Number of Drivers:** An integer, `D`, representing the number of drivers available.
*   **Maximum Route Duration:** An integer, `T`, representing the maximum time (in minutes) a driver can spend on a single route.
*   **Congestion Threshold:** An integer, `C`, representing the maximum acceptable total congestion score for a route.

**Objective:**

For each delivery request, determine the optimal route (if one exists) that minimizes a weighted sum of travel time and congestion score, subject to the following constraints:

1.  **Route Validity:** The route must be a valid path in the city graph, starting from the `start_node_id` and ending at the `end_node_id` for each delivery request.
2.  **Time Constraint:** The total travel time of the route must not exceed the `Maximum Route Duration` `T`.
3.  **Congestion Constraint:** The total congestion score of the route must not exceed the `Congestion Threshold` `C`.
4.  **Optimization Metric:** Minimize `alpha * total_travel_time + (1 - alpha) * total_congestion_score`, where `alpha` is a weight parameter between 0 and 1 (inclusive), given as input.

**Output:**

A list of optimal routes, one for each delivery request, in the same order as the input requests. Each route should be represented as a list of node IDs, starting with the `start_node_id` and ending with the `end_node_id`. If no valid route exists for a given delivery request, return an empty list `[]`.

**Constraints:**

*   1 <= `N` <= 500 (Number of nodes in the city graph)
*   1 <= `M` <= 5000 (Number of edges in the city graph)
*   1 <= `D` <= 10 (Number of drivers)
*   1 <= `T` <= 1000 (Maximum Route Duration)
*   0 <= `C` <= 5000 (Congestion Threshold)
*   0 <= `alpha` <= 1 (Weight parameter)
*   1 <= `priority` <= 10 (Delivery request priority)
*   Travel time for each street segment is between 1 and 100 minutes (inclusive).
*   Congestion score for each street segment is between 0 and 100 (inclusive).

**Efficiency Requirements:**

The solution should be efficient enough to handle large city graphs and a significant number of delivery requests within a reasonable time limit (e.g., under 1 minute for a moderate-sized input). Consider using appropriate data structures and algorithms to optimize performance.

**Edge Cases:**

*   The graph might not be fully connected.
*   There might be no path between the `start_node_id` and `end_node_id` for some delivery requests.
*   Multiple optimal routes might exist. In such cases, return any one of them.
*   The start and end nodes of a delivery request might be the same.

This problem requires a combination of graph traversal algorithms, optimization techniques, and careful handling of constraints to arrive at an efficient solution. Think about using Dijkstra's or A\* algorithm with modifications to account for the congestion score and the time/congestion constraints. Dynamic programming approaches might also be considered.  Good luck!
