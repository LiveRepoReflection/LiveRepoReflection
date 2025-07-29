## Problem: Optimal Traffic Flow Reconfiguration

**Question Description:**

A major metropolitan area is experiencing a severe traffic congestion crisis. The city's road network can be represented as a directed graph where nodes represent intersections and directed edges represent road segments with associated capacities (maximum number of vehicles that can pass through the road segment per unit time).

The city has a central traffic control system that can dynamically adjust the road network by:

1.  **Re-routing traffic:** Modifying the flow of traffic through the existing road network.
2.  **Temporarily closing roads:** Reducing the capacity of specific road segments to zero.
3.  **Temporarily opening roads:** Increasing the capacity of specific road segments. (For simplicity, capacity can only be increased to the original design capacity).

The city has identified a set of critical origin-destination (OD) pairs, each with a specific demand (number of vehicles that need to travel between the OD pair per unit time). The goal is to minimize the total travel time for all vehicles across all OD pairs by optimally reconfiguring the traffic flow and potentially adjusting road capacities.

**Specifically, you are given:**

*   `n`: The number of intersections (nodes) in the road network, numbered from 0 to n-1.
*   `edges`: A list of tuples, where each tuple `(u, v, capacity, travel_time)` represents a directed road segment from intersection `u` to intersection `v` with a maximum `capacity` and `travel_time` (time taken to traverse the road segment).
*   `od_pairs`: A list of tuples, where each tuple `(origin, destination, demand)` represents an origin-destination pair with a specified `demand`.
*   `max_capacity_changes`: An integer representing the maximum number of road segments whose capacity can be changed (either reduced to 0 or increased back to their original capacity).

**Your task is to determine:**

1.  The optimal configuration of traffic flow through the network *and* the optimal set of capacity changes (within the `max_capacity_changes` constraint) that minimizes the total travel time for all vehicles across all OD pairs.
2.  The minimum total travel time achievable with this optimal configuration.

**Constraints:**

*   1 <= `n` <= 100
*   1 <= len(`edges`) <= 500
*   1 <= capacity <= 100
*   1 <= travel\_time <= 100
*   1 <= len(`od_pairs`) <= 10
*   1 <= demand <= 100
*   0 <= `max_capacity_changes` <= 10
*   All graph edges must have non-negative capacities.
*   The total flow for each OD pair must equal its demand.
*   The flow on each road segment must not exceed its capacity.
*   Assume there is at least one feasible solution.
*   Assume there is no storage (vehicles do not accumulate at intersections).

**Input:**

*   `n`: Integer
*   `edges`: List of tuples `(u, v, capacity, travel_time)`
*   `od_pairs`: List of tuples `(origin, destination, demand)`
*   `max_capacity_changes`: Integer

**Output:**

*   The minimum total travel time achievable (integer).

**Example:**

```python
n = 4
edges = [(0, 1, 10, 5), (0, 2, 15, 3), (1, 3, 7, 4), (2, 3, 12, 2)]
od_pairs = [(0, 3, 8)]
max_capacity_changes = 1
```

**Scoring:**

*   Solutions will be evaluated based on correctness and efficiency.
*   Solutions that use approximation algorithms or heuristics will be accepted, but may receive lower scores than optimal solutions.
*   Test cases will include small, medium, and large-sized road networks with varying degrees of congestion.

**Hints:**

*   This problem can be approached using a combination of network flow algorithms, optimization techniques, and potentially heuristics.
*   Consider using the min-cost max-flow algorithm to find the optimal traffic flow for a given network configuration.
*   Think about how to efficiently explore the space of possible capacity changes within the `max_capacity_changes` constraint.
*   Dynamic programming or branch and bound techniques might be helpful for exploring the capacity change space.
*   Be mindful of time complexity, as exhaustive search will likely be too slow for larger test cases.
