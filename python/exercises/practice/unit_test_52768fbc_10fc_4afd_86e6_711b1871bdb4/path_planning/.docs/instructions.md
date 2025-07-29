## Project Name

`OptimalPathPlanning`

## Question Description

You are tasked with developing an optimal path planning algorithm for autonomous vehicles navigating a complex, dynamic urban environment represented as a weighted graph.

The city consists of `N` intersections (nodes) and `M` bidirectional roads (edges). Each road has an associated cost representing travel time, fuel consumption, and safety risk. This cost is dynamic and changes over time based on real-time traffic conditions and weather forecasts. Each road also has a capacity, limiting the number of vehicles that can simultaneously use it.

Your autonomous vehicle needs to travel from a starting intersection `S` to a destination intersection `D` within a specified time window `[T_start, T_end]`.

**Specific Requirements:**

1.  **Dynamic Edge Costs:** The cost of traversing a road changes dynamically based on time. You will be provided with a function `get_edge_cost(u, v, t)` that returns the cost of traveling from intersection `u` to intersection `v` at time `t`. This cost can vary significantly. Assume travel along an edge takes negligible time.

2.  **Capacity Constraints:** Each road has a maximum capacity. You need to ensure that the planned path doesn't exceed the capacity of any road at any point in time. A function `get_edge_capacity(u,v,t)` will return the available capacity of the road from `u` to `v` at time `t`. If the path planning algorithm determines that the edge is at full capacity, the agent must not use the edge at that time.

3.  **Time Window:** The vehicle must reach the destination intersection `D` within the specified time window `[T_start, T_end]`. Arriving before `T_start` or after `T_end` is considered a failure.

4.  **Optimization Goal:** The primary goal is to minimize the *total cost* of the path while adhering to the capacity constraints and the time window. The secondary goal is to minimize the travel time if multiple paths have the same minimal cost.

5.  **Lookahead:** Your algorithm should incorporate a lookahead mechanism to anticipate future cost changes and capacity constraints. A lookahead window `L` determines how far into the future your algorithm should consider when making path planning decisions.

6.  **Real-World Constraints:** The city graph can be large (up to 1000 intersections and 5000 roads). The dynamic edge costs and capacities can change rapidly. Your algorithm needs to be efficient enough to compute a near-optimal path in a reasonable amount of time (e.g., under 1 second).

7.  **Edge Case Handling:** Handle cases where no path exists within the time window, or all possible paths violate capacity constraints.

**Input:**

*   `N`: Number of intersections (nodes).
*   `M`: Number of roads (edges).
*   `graph`: A list of tuples `(u, v, cost)` representing the initial road network, where `u` and `v` are intersection IDs (0 to N-1), and `cost` is the initial cost.
*   `S`: Starting intersection ID.
*   `D`: Destination intersection ID.
*   `T_start`: Start time.
*   `T_end`: End time.
*   `L`: Lookahead window size (in time units).
*   `get_edge_cost(u, v, t)`: A function that returns the cost of traveling from intersection `u` to intersection `v` at time `t`.
*   `get_edge_capacity(u, v, t)`: A function that returns the available capacity of the road from `u` to `v` at time `t`.

**Output:**

*   A list of intersection IDs representing the optimal path from `S` to `D`, or an empty list `[]` if no valid path is found. If multiple optimal paths exist, return the path with the shortest travel time.

**Constraints:**

*   1 <= `N` <= 1000
*   1 <= `M` <= 5000
*   0 <= `S`, `D` < `N`
*   0 <= `T_start` < `T_end` <= 1000
*   1 <= `L` <= 100
*   The graph is connected.

**Judging Criteria:**

*   Correctness: Does your algorithm find a valid path when one exists?
*   Optimality: Is the path found close to the optimal path (minimum cost)?
*   Efficiency: Does the algorithm run within the time limit?
*   Robustness: Does the algorithm handle edge cases gracefully?
*   Code Quality: Is the code well-structured, readable, and maintainable?
