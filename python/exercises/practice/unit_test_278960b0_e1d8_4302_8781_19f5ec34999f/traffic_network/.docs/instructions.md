Okay, here is a challenging Python coding problem designed to be similar to LeetCode Hard level.

### Project Name

```
Traffic-Optimization-Network
```

### Question Description

Imagine you are designing a smart traffic management system for a city. The city's road network can be represented as a directed graph, where nodes are intersections and edges are road segments. Each road segment has a length (in meters) and a capacity (maximum number of vehicles that can traverse it per second).

During peak hours, traffic congestion can occur. To alleviate this, your system can dynamically adjust the speed limit on each road segment, impacting both the capacity and the travel time.

**Specifically:**

1.  **Road Network:** The road network is represented as a dictionary where keys are intersection IDs (integers), and values are lists of tuples. Each tuple represents a road segment emanating from that intersection, with the format: `(destination_intersection_id, length, base_capacity)`.  `base_capacity` is the road segment's capacity at the *default* speed limit.

2.  **Speed Limit Adjustment:**  Your system can adjust the speed limit on each road segment.  Increasing the speed limit increases the capacity (vehicles/second) but also increases the risk of accidents, modeled as a congestion penalty.  Decreasing the speed limit reduces capacity but also reduces the congestion penalty.

    *   **Capacity Scaling:** The effective capacity of a road segment is calculated as `effective_capacity = base_capacity * (speed_limit / default_speed_limit)`.  The `speed_limit` and `default_speed_limit` are represented as floats (e.g., 0.8 represents 80% of the default).

    *   **Travel Time:** The travel time (in seconds) for a road segment is calculated as `travel_time = length / (default_speed_limit * speed_limit)`. Remember to keep the units consistent (length in meters, speed in meters per second).

    *   **Congestion Penalty:**  The congestion penalty for a road segment is calculated as `congestion_penalty = utilization_rate**penalty_exponent`.  The `utilization_rate` is `current_flow / effective_capacity`, `current_flow` is the number of vehicles currently using the segment, and `penalty_exponent` is a given parameter (e.g., 2 for a quadratic penalty).  If the `utilization_rate` exceeds 1, the congestion_penalty is infinite.

3.  **Optimization Goal:** Given a source intersection, a destination intersection, a total traffic flow (vehicles per second) that needs to travel from source to destination, the road network, the default speed limit, the penalty exponent, and a maximum allowed total congestion penalty, your task is to determine the optimal speed limit for *each* road segment along the shortest path from source to destination such that:

    *   The total traffic flow can be accommodated (i.e., no road segment's capacity is exceeded given its adjusted speed limit).
    *   The shortest path from source to destination is calculated based on the *travel time* of each segment, given adjusted speed limits.
    *   The total congestion penalty across all road segments on the shortest path does not exceed the given maximum allowed penalty.  The total congestion penalty is the sum of individual segment congestion penalties.
    *   The speed limit for each road segment must be within the range `0.5 <= speed_limit <= 1.5` times the `default_speed_limit`.

4.  **Constraints:**

    *   The graph can be large (up to 1000 intersections and 5000 road segments).
    *   The total traffic flow can be high (up to 1000 vehicles/second).
    *   Finding the absolute optimal speed limit configuration might be computationally infeasible within a reasonable time. Aim for a *good* solution that satisfies the constraints and minimizes travel time.
    *   The road network is not guaranteed to be fully connected. There may be no path between the source and destination.
    *   Multiple shortest paths may exist; your solution should work correctly for any of them.
    *   You can assume all inputs are valid (positive lengths and capacities, valid intersection IDs, etc.).

5.  **Input:**

    *   `network`: A dictionary representing the road network (described above).
    *   `source`: The ID of the source intersection (integer).
    *   `destination`: The ID of the destination intersection (integer).
    *   `total_flow`: The total traffic flow (vehicles per second) (float).
    *   `default_speed_limit`: The default speed limit (meters per second) (float).
    *   `penalty_exponent`: The exponent for the congestion penalty calculation (float).
    *   `max_penalty`: The maximum allowed total congestion penalty (float).

6.  **Output:**

    *   A dictionary where keys are tuples `(start_intersection_id, end_intersection_id)` representing a road segment on the shortest path, and values are the optimal speed limit for that segment (float).  If no path exists or no feasible speed limit configuration can be found within the constraints, return an empty dictionary.  The segment order is implied by the shortest path discovered.

This problem requires a combination of graph algorithms (shortest path finding), optimization techniques (potentially heuristics or approximation algorithms), and careful handling of constraints.  It is designed to be challenging and to encourage exploration of different algorithmic approaches. Good luck!
