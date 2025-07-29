## The "Optimal Traffic Routing" Problem

**Problem Description:**

Imagine you are designing a traffic routing system for a smart city. The city's road network is represented as a directed graph, where nodes are intersections and edges are road segments. Each road segment has a capacity (maximum number of vehicles it can handle per unit time) and a current flow (number of vehicles currently using it per unit time).

Given a set of source-destination pairs (traffic requests) with specified traffic demands (number of vehicles that need to travel from source to destination per unit time), your task is to design an algorithm that optimally routes the traffic to minimize the overall traffic congestion in the city.

**Specifically:**

*   **Input:**
    *   `N`: The number of intersections (nodes) in the city (indexed from 0 to N-1).
    *   `edges`: A list of tuples, where each tuple `(u, v, capacity, flow)` represents a directed road segment from intersection `u` to intersection `v` with a specified `capacity` and current `flow`. `0 <= u, v < N`.
    *   `requests`: A list of tuples, where each tuple `(source, destination, demand)` represents a traffic request with `demand` vehicles needing to travel from intersection `source` to intersection `destination`. `0 <= source, destination < N`.
*   **Output:**
    *   A list of dictionaries, where each dictionary corresponds to a request in the `requests` list and specifies the flow allocation across different paths for that request. Each dictionary represents the routing solution for each request. The Dictionary will have the following format:

        ```json
        [
        	{
        		"path": [0, 1, 2],
        		"flow": 5
        	},
        	{
        		"path": [0, 3, 2],
        		"flow": 3
        	}
        ]
        ```
        *The sum of all flow values in the dictionary should be equal to the request's demand. Each path should be valid path between source and destination.*
*   **Objective:**

    Minimize the maximum congestion ratio across all road segments.  The congestion ratio for a road segment is defined as `(current_flow + additional_flow) / capacity`, where `additional_flow` is the increase in flow due to your routing decisions.  The overall objective is to minimize the *maximum* of these congestion ratios across *all* edges.  This ensures that no single road segment is overly congested.

**Constraints and Considerations:**

1.  **Capacity Constraints:** The flow on each road segment (current flow + additional flow) must not exceed its capacity.
2.  **Flow Conservation:** For each intersection (except source and destination for each request), the total inflow must equal the total outflow.
3.  **Multiple Paths:**  A single request can be split across multiple paths from source to destination. The solution must specify the flow allocation for each path.
4.  **Graph Structure:** The road network graph might not be fully connected. There might not be a path between some source-destination pairs. In such cases, the request should be skipped.
5.  **Optimization:** Finding the absolutely optimal solution might be computationally expensive. The solution should aim for a near-optimal solution within a reasonable time limit (e.g., a few seconds).
6.  **Scalability:** The algorithm should be reasonably efficient for road networks with a moderate number of intersections (e.g., up to 100) and requests.
7.  **Numerical Precision:** Handle potential floating-point precision issues when calculating congestion ratios.
8.  **Tie Breaking:** If multiple routing solutions lead to the same maximum congestion ratio, provide a solution that distributes the traffic more evenly across available paths.

**Edge Cases:**

*   Zero capacity edges.
*   Zero demand requests.
*   Source and destination are the same.
*   Cyclical dependencies in the graph.

**Judging Criteria:**

The solution will be judged based on:

1.  **Correctness:** The solution must satisfy all constraints (capacity, flow conservation). The suggested paths should be valid and connect the source to the destination.
2.  **Optimality:** The solution should minimize the maximum congestion ratio across all road segments.
3.  **Efficiency:** The solution should run within a reasonable time limit.
4.  **Code Quality:** The code should be well-structured, readable, and maintainable.

This problem requires a combination of graph algorithms (e.g., finding paths, maximum flow), optimization techniques (e.g., binary search, linear programming approximation), and careful handling of constraints and edge cases. Good luck!
